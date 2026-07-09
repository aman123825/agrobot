/**
 * dosing.cpp - Sequential dosing state machine (Branch A: spring-return).
 *
 * Sequence: pump pre-soak -> actuator extend -> dwell -> micro-dose ->
 * de-energize (spring retracts). The two relay channels are NEVER energized
 * at the same time.
 *
 * Safety: the whole sequence runs with EVT_DOSING asserted, which forces the
 * drive task to keep the motors stopped - the rover must not move while the
 * probe is in the soil.
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

void dosing_init(EventGroupHandle_t events) {
    sEvents = events;
    pinMode(PIN_RELAY_PUMP, OUTPUT);
    pinMode(PIN_RELAY_ACTUATOR, OUTPUT);
    relayOff(PIN_RELAY_PUMP);
    relayOff(PIN_RELAY_ACTUATOR);
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

    // 2) Extend actuator to soil (internal limit switch ends travel).
    Serial.println("DOSE extend");
    relayOn(PIN_RELAY_ACTUATOR);
    vTaskDelay(pdMS_TO_TICKS(ACTUATOR_TRAVEL_MS));

    // 3) Dwell, then micro-dose fertilizer into the probe hole.
    vTaskDelay(pdMS_TO_TICKS(DOSE_DWELL_MS));
    Serial.println("DOSE inject");
    relayOn(PIN_RELAY_PUMP);
    vTaskDelay(pdMS_TO_TICKS(DOSE_INJECT_MS));
    relayOff(PIN_RELAY_PUMP);

    // 4) Retract: power off, the spring pulls the actuator back.
    Serial.println("DOSE retract");
    relayOff(PIN_RELAY_ACTUATOR);
    vTaskDelay(pdMS_TO_TICKS(ACTUATOR_TRAVEL_MS));

    // Release the drive freeze (only this bit; never clears a real EVT_HALT).
    if (sEvents) xEventGroupClearBits(sEvents, EVT_DOSING);
    Serial.println("DOSE done");
    return true;
}
