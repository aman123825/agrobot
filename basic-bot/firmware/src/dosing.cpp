/**
 * dosing.cpp - Sequential dosing state machine (MG995 servo insertion).
 *
 * Sequence: pump pre-soak -> servo lowers the probe into the soil -> dwell ->
 * micro-dose -> servo raises the probe back to the travel position. The whole
 * sequence runs with EVT_DOSING asserted, which forces the drive task to keep
 * the motors stopped - the rover must not move while the probe is in the soil.
 *
 * The insertion servo (combined NPK + moisture probe) is an MG995 positional
 * servo on PIN_SERVO_INSERT, driven directly with LEDC at 50 Hz on a dedicated
 * channel (LEDC_CH_SERVO / timer 2) so it never disturbs the drive PWM
 * (channels 0-3). Calibrate SERVO_INSERT_UP_DEG / SERVO_INSERT_DOWN_DEG in
 * config.h before running this against real soil.
 */
#include <Arduino.h>
#include "pins.h"
#include "config.h"
#include "events.h"
#include "dosing.h"

#if RELAY_ACTIVE_LOW
static inline void relayOn(uint8_t pin)  { digitalWrite(pin, LOW); }
static inline void relayOff(uint8_t pin) { digitalWrite(pin, HIGH); }
#else
static inline void relayOn(uint8_t pin)  { digitalWrite(pin, HIGH); }
static inline void relayOff(uint8_t pin) { digitalWrite(pin, LOW); }
#endif

static EventGroupHandle_t sEvents = nullptr;
static int sServoDeg = SERVO_INSERT_UP_DEG;   // last commanded servo angle

// ---- Insertion servo (LEDC @ 50 Hz on LEDC_CH_SERVO) ----
// Convert an angle (0..180 deg) to an LEDC duty count for the configured
// pulse-width range and frame period.
static uint32_t servoDutyForDeg(int deg) {
    deg = constrain(deg, 0, 180);
    uint32_t us = SERVO_MIN_US +
                  (uint32_t)((long)(SERVO_MAX_US - SERVO_MIN_US) * deg / 180L);
    const uint32_t maxDuty  = (1UL << LEDC_SERVO_RES_BITS) - 1UL;
    const uint32_t periodUs = 1000000UL / LEDC_SERVO_FREQ_HZ;   // 20000 us @ 50 Hz
    return (uint32_t)(((uint64_t)us * maxDuty) / periodUs);
}

static void servoWrite(int deg) {
    sServoDeg = constrain(deg, 0, 180);
    ledcWrite(LEDC_CH_SERVO, servoDutyForDeg(sServoDeg));
}

// Move to the target angle in small steps so the probe eases in/out instead of
// slamming (gentler on the linkage and easier on the 5V rail).
static void servoSweepTo(int target) {
    target = constrain(target, 0, 180);
    int step = (target >= sServoDeg) ? SERVO_STEP_DEG : -SERVO_STEP_DEG;
    while (sServoDeg != target) {
        int next = sServoDeg + step;
        if ((step > 0 && next > target) || (step < 0 && next < target)) next = target;
        servoWrite(next);
        vTaskDelay(pdMS_TO_TICKS(SERVO_STEP_MS));
    }
}

void dosing_init(EventGroupHandle_t events) {
    sEvents = events;

    // Pump relay off (active-LOW module -> pin HIGH).
    pinMode(PIN_RELAY_PUMP, OUTPUT);
    relayOff(PIN_RELAY_PUMP);

    // Attach the servo and hold the retracted (UP) travel position.
    ledcSetup(LEDC_CH_SERVO, LEDC_SERVO_FREQ_HZ, LEDC_SERVO_RES_BITS);
    ledcAttachPin(PIN_SERVO_INSERT, LEDC_CH_SERVO);
    sServoDeg = SERVO_INSERT_UP_DEG;
    servoWrite(SERVO_INSERT_UP_DEG);
}

bool dosing_run_sequence() {
    if (sEvents && (xEventGroupGetBits(sEvents) & EVT_PUMP_DISABLE)) {
        Serial.println("DOSE blocked (pump disabled)");
        return false;
    }

    // Freeze the drive for the entire insertion.
    if (sEvents) xEventGroupSetBits(sEvents, EVT_DOSING);
    Serial.println("DOSE start");

    // 1) Pre-soak: soften the soil so insertion stays under the lift threshold.
    Serial.println("DOSE presoak");
    relayOn(PIN_RELAY_PUMP);
    vTaskDelay(pdMS_TO_TICKS(DOSE_PRESOAK_MS));
    relayOff(PIN_RELAY_PUMP);

    // 2) Lower the probe into the soil (stepped, gentle).
    Serial.println("DOSE insert");
    servoSweepTo(SERVO_INSERT_DOWN_DEG);

    // 3) Dwell, then micro-dose fertilizer into the probe hole.
    vTaskDelay(pdMS_TO_TICKS(DOSE_DWELL_MS));
    Serial.println("DOSE inject");
    relayOn(PIN_RELAY_PUMP);
    vTaskDelay(pdMS_TO_TICKS(DOSE_INJECT_MS));
    relayOff(PIN_RELAY_PUMP);

    // 4) Raise the probe back to the travel position.
    Serial.println("DOSE retract");
    servoSweepTo(SERVO_INSERT_UP_DEG);

    // Release the drive freeze (only this bit; never clears a real EVT_HALT).
    if (sEvents) xEventGroupClearBits(sEvents, EVT_DOSING);
    Serial.println("DOSE done");
    return true;
}


// ---- Manual probe control (independent of the full DOSE cycle) ----
// Lower/raise the NPK+moisture probe with the same gentle stepped sweep used by
// the dose sequence. Lowering asserts EVT_DOSING so the drive stays frozen while
// the probe is in the soil; raising clears it. These run on the sensor task
// (never the web callback), so the blocking sweep can't stall the server.
void dosing_probe_down() {
    if (sEvents) xEventGroupSetBits(sEvents, EVT_DOSING);
    Serial.println("PROBE down");
    servoSweepTo(SERVO_INSERT_DOWN_DEG);
}

void dosing_probe_up() {
    Serial.println("PROBE up");
    servoSweepTo(SERVO_INSERT_UP_DEG);
    if (sEvents) xEventGroupClearBits(sEvents, EVT_DOSING);
}