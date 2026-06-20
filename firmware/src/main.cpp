/**
 * main.cpp - AgriRover ESP32 entry point.
 *
 * Dual-core FreeRTOS layout (BOM #91):
 *   Core 1 -> driveTask   : motor PWM + obstacle reaction (high rate)
 *   Core 0 -> sensorTask  : NPK/ambient polling, dosing sequence, MQTT publish
 *
 * Inter-core signaling uses an EventGroup (not volatile bools) so halt/resume
 * and low-battery events are observed atomically across cores.
 */
#include <Arduino.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"

#include "pins.h"
#include "config.h"
#include "events.h"
#include "drive.h"
#include "sensors.h"
#include "servo.h"
#include "dosing.h"
#include "comms.h"

// ---- Cross-core event group (bits live in events.h) ----
EventGroupHandle_t gEvents;

// Fail-safe: force both dosing relays OFF immediately, before tasks start.
// The relay module is active-LOW, so OFF == drive the pin HIGH. This closes the
// boot window where the pins float and could energize the pump/actuator.
// (External 10k pull-ups to 3.3V on these pins are still required - see §5.2.)
static void relaysFailSafeOff() {
    pinMode(PIN_RELAY_PUMP, OUTPUT);
    digitalWrite(PIN_RELAY_PUMP, HIGH);
    pinMode(PIN_RELAY_ACTUATOR, OUTPUT);
    digitalWrite(PIN_RELAY_ACTUATOR, HIGH);
}

static void driveTask(void *pv) {
    drive_init();
    for (;;) {
        comms_poll_pi();  // read Pi commands EVERY loop so STOP/tilt-halt are honored fast
        EventBits_t bits = xEventGroupGetBits(gEvents);
        if (bits & EVT_DRIVE_INHIBIT) {   // halt | low-battery | dosing-in-progress
            drive_stop();
        } else {
            drive_update();  // applies current velocity target + obstacle avoidance
        }
        vTaskDelay(pdMS_TO_TICKS(20));  // 50 Hz control loop
    }
}

static void sensorTask(void *pv) {
    sensors_init();
    servo_us_init();   // ultrasonic sweep mount (centered on startup)
    dosing_init(gEvents);
    for (;;) {
        sensors_poll();          // NPK (Modbus), DHT22, moisture, TDS, GPS, battery
        comms_publish_telemetry();
        if (xEventGroupGetBits(gEvents) & EVT_DOSE_REQUEST) {
            dosing_run_sequence();  // sets EVT_DOSING internally so the drive halts
            xEventGroupClearBits(gEvents, EVT_DOSE_REQUEST);
        }
        vTaskDelay(pdMS_TO_TICKS(200));  // 5 Hz sensor loop
    }
}

void setup() {
    Serial.begin(115200);
    relaysFailSafeOff();   // FIRST: guarantee pump + actuator are off at boot

    gEvents = xEventGroupCreate();

    comms_init(gEvents);   // WiFi + MQTT + UART link to Pi; routes Pi commands to events

    xTaskCreatePinnedToCore(driveTask,  "drive",  TASK_STACK_WORDS, nullptr, 2,
                            nullptr, TASK_DRIVE_CORE);
    xTaskCreatePinnedToCore(sensorTask, "sensor", TASK_STACK_WORDS, nullptr, 1,
                            nullptr, TASK_SENSOR_CORE);
}

void loop() {
    // Everything runs in FreeRTOS tasks; keep loop() idle.
    vTaskDelay(pdMS_TO_TICKS(1000));
}
