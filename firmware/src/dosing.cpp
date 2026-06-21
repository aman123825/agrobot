/**
 * dosing.cpp - Sequential dosing state machine (circuit §5.2).
 *
 * Relay channels are active per the 2-channel module's opto logic. The two
 * channels are NEVER energized at the same time - that was the fix for the
 * original single-relay design.
 *
 * Safety: the whole sequence runs with EVT_DOSING asserted, which forces the
 * drive task to keep the motors stopped. The rover must not move while the
 * actuator/probe is in the soil.
 *
 * Actuator retraction (FC-03, config.h ACTUATOR_DC_REVERSIBLE):
 *   Branch A (spring-return, flag=0, default): de-energizing Ch2 retracts.
 *   Branch B (DC reversible, flag=1): a DPDT relay on PIN_ACTUATOR_DIR flips
 *                             polarity to actively drive the retract phase.
 *                             Compiles both ways; see pins.h / config.h.
 */
#include <Arduino.h>
#include "pins.h"
#include "config.h"
#include "events.h"
#include "dosing.h"

// Relay module is active-LOW (LOW = energized). Confirm against your module.
static inline void relayOn(uint8_t pin)  { digitalWrite(pin, LOW); }
static inline void relayOff(uint8_t pin) { digitalWrite(pin, HIGH); }

static EventGroupHandle_t sEvents = nullptr;

void dosing_init(EventGroupHandle_t events) {
    sEvents = events;
    pinMode(PIN_RELAY_PUMP, OUTPUT);
    pinMode(PIN_RELAY_ACTUATOR, OUTPUT);
    relayOff(PIN_RELAY_PUMP);
    relayOff(PIN_RELAY_ACTUATOR);
#if ACTUATOR_DC_REVERSIBLE
    // Branch B: DPDT direction line idles LOW (extend polarity).
    pinMode(PIN_ACTUATOR_DIR, OUTPUT);
    digitalWrite(PIN_ACTUATOR_DIR, LOW);
#endif
}

bool dosing_run_sequence() {
    // Abort if dosing is blocked (e.g. tank empty / Pi override).
    if (sEvents && (xEventGroupGetBits(sEvents) & EVT_PUMP_DISABLE)) {
        return false;
    }

    // Freeze the drive for the entire insertion. driveTask sees EVT_DOSING in
    // EVT_DRIVE_INHIBIT and holds the motors stopped.
    if (sEvents) xEventGroupSetBits(sEvents, EVT_DOSING);

    // 1) Pre-soak: pump softens soil so insertion stays under the lift threshold.
    relayOn(PIN_RELAY_PUMP);
    vTaskDelay(pdMS_TO_TICKS(DOSE_PRESOAK_MS));
    relayOff(PIN_RELAY_PUMP);

    // 2) Extend actuator to soil (internal limit switch ends travel).
    relayOn(PIN_RELAY_ACTUATOR);
    vTaskDelay(pdMS_TO_TICKS(ACTUATOR_TRAVEL_MS));

    // 3) Dwell, then micro-dose fertilizer into the probe hole.
    vTaskDelay(pdMS_TO_TICKS(DOSE_DWELL_MS));
    relayOn(PIN_RELAY_PUMP);
    vTaskDelay(pdMS_TO_TICKS(DOSE_INJECT_MS));
    relayOff(PIN_RELAY_PUMP);

    // 4) Retract.
#if ACTUATOR_DC_REVERSIBLE
    // Branch B (DC reversible): set the DPDT direction line to reverse polarity,
    // then power Ch2 to actively drive the actuator back (limit switch ends it),
    // then de-energize and restore the extend polarity.
    digitalWrite(PIN_ACTUATOR_DIR, HIGH);
    relayOn(PIN_RELAY_ACTUATOR);
    vTaskDelay(pdMS_TO_TICKS(ACTUATOR_TRAVEL_MS));
    relayOff(PIN_RELAY_ACTUATOR);
    digitalWrite(PIN_ACTUATOR_DIR, LOW);
#else
    // Branch A (spring-return): power off = spring pulls the actuator back.
    relayOff(PIN_RELAY_ACTUATOR);
    vTaskDelay(pdMS_TO_TICKS(ACTUATOR_TRAVEL_MS));
#endif

    // Release the drive freeze (only this bit; never clears a real EVT_HALT).
    if (sEvents) xEventGroupClearBits(sEvents, EVT_DOSING);
    return true;
}
