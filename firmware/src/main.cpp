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
#include "drive.h"
#include "sensors.h"
#include "dosing.h"
#include "comms.h"

// ---- Cross-core event bits ----
EventGroupHandle_t gEvents;
#define EVT_HALT          (1 << 0)  // e-stop / tilt / obstacle -> stop motors
#define EVT_LOW_BATTERY   (1 << 1)  // LiPo below cutoff -> return-to-base
#define EVT_DOSE_REQUEST  (1 << 2)  // waypoint reached -> run dosing sequence
#define EVT_PAUSE_IRRIG   (1 << 3)  // rain detected (relayed from Pi)

static void driveTask(void *pv) {
    drive_init();
    for (;;) {
        EventBits_t bits = xEventGroupGetBits(gEvents);
        if (bits & (EVT_HALT | EVT_LOW_BATTERY)) {
            drive_stop();
        } else {
            drive_update();  // applies current velocity target + obstacle avoidance
        }
        vTaskDelay(pdMS_TO_TICKS(20));  // 50 Hz control loop
    }
}

static void sensorTask(void *pv) {
    sensors_init();
    dosing_init();
    for (;;) {
        sensors_poll();          // NPK (Modbus), DHT22, moisture, TDS, GPS, battery
        comms_publish_telemetry();
        if (xEventGroupGetBits(gEvents) & EVT_DOSE_REQUEST) {
            dosing_run_sequence();  // pump pre-soak -> actuator -> dose -> retract
            xEventGroupClearBits(gEvents, EVT_DOSE_REQUEST);
        }
        vTaskDelay(pdMS_TO_TICKS(200));  // 5 Hz sensor loop
    }
}

void setup() {
    Serial.begin(115200);
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
