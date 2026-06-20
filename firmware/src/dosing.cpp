/**
 * dosing.cpp - Sequential dosing state machine (circuit §5.2).
 *
 * Relay channels are active per the 2-channel module's opto logic. The two
 * channels are NEVER energized at the same time - that was the fix for the
 * original single-relay design.
 *
 * Actuator retraction (OPEN ITEM):
 *   Branch A (spring-return): de-energizing Ch2 retracts. Implemented below.
 *   Branch B (DC reversible): add PIN_ACTUATOR_DIR + DPDT relay, flip polarity
 *                             before the retract phase. See pins.h.
 */
#include <Arduino.h>
#include "pins.h"
#include "config.h"
#include "dosing.h"

// Relay module is typically active-LOW; adjust if your module differs.
static inline void relayOn(uint8_t pin)  { digitalWrite(pin, LOW); }
static inline void relayOff(uint8_t pin) { digitalWrite(pin, HIGH); }

void dosing_init() {
    pinMode(PIN_RELAY_PUMP, OUTPUT);
    pinMode(PIN_RELAY_ACTUATOR, OUTPUT);
    relayOff(PIN_RELAY_PUMP);
    relayOff(PIN_RELAY_ACTUATOR);
}

bool dosing_run_sequence() {
    // TODO: check float-sensor / PUMP_DISABLE flag relayed from Pi before starting.

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

    // 4) Retract.  Branch A: power off = spring return.
    relayOff(PIN_RELAY_ACTUATOR);
    // Branch B would set PIN_ACTUATOR_DIR for reverse polarity here.
    vTaskDelay(pdMS_TO_TICKS(ACTUATOR_TRAVEL_MS));

    return true;
}
