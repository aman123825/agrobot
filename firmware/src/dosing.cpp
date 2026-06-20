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
 * Actuator retraction (OPEN ITEM):
 *   Branch A (spring-return): de-energizing Ch2 retracts. Implemented below.
 *   Branch B (DC reversible): add PIN_ACTUATOR_DIR + DPDT relay, flip polarity
 *                             before the retract phase. See pins.h.
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
}

bool dosing_run_sequence() {
    // TODO: check float-sensor / PUMP_DISABLE flag relayed from Pi before starting.

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

    // 4) Retract.  Branch A: power off = spring return.
    relayOff(PIN_RELAY_ACTUATOR);
    // Branch B would set PIN_ACTUATOR_DIR for reverse polarity here.
    vTaskDelay(pdMS_TO_TICKS(ACTUATOR_TRAVEL_MS));

    // Release the drive freeze (only this bit; never clears a real EVT_HALT).
    if (sEvents) xEventGroupClearBits(sEvents, EVT_DOSING);
    return true;
}
