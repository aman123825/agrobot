/**
 * main.cpp - AgriRover BASIC BOT entry point (ESP32-only, no AI / no Pi).
 *
 * Dual-core FreeRTOS layout (same shape as the full firmware):
 *   Core 1 -> driveTask  : serial commands + motor PWM + dead-man (50 Hz)
 *   Core 0 -> sensorTask : ultrasonic @5 Hz; NPK/DHT/moisture/battery +
 *                          telemetry @1 Hz; dosing sequence on request
 *
 * Inter-core signaling uses an EventGroup so halt/obstacle/dosing states are
 * observed atomically across cores.
 */
#include <Arduino.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"
#include "esp_task_wdt.h"

#include "pins.h"
#include "config.h"
#include "events.h"
#include "drive.h"
#include "sensors.h"
#include "dosing.h"
#include "commands.h"
#include "telemetry.h"

EventGroupHandle_t gEvents;

// Fail-safe: force both dosing relays OFF immediately, before tasks start.
// Active-LOW module: OFF == pin HIGH. Closes the boot window where floating
// pins could energize the pump/actuator. (External 10k pull-ups to 3.3V on
// GPIO13/26 are still required to cover the time before setup() runs.)
static void relaysFailSafeOff() {
    pinMode(PIN_RELAY_PUMP, OUTPUT);
    pinMode(PIN_RELAY_ACTUATOR, OUTPUT);
#if RELAY_ACTIVE_LOW
    digitalWrite(PIN_RELAY_PUMP, HIGH);
    digitalWrite(PIN_RELAY_ACTUATOR, HIGH);
#else
    digitalWrite(PIN_RELAY_PUMP, LOW);
    digitalWrite(PIN_RELAY_ACTUATOR, LOW);
#endif
}

static void driveTask(void* pv) {
    drive_init();
    esp_task_wdt_add(NULL);
    bool deadmanStopped = false;

    for (;;) {
        esp_task_wdt_reset();
        commands_poll();   // every loop so STOP is honored fast

        int16_t l, r;
        drive_get(&l, &r);

        // Dead-man: setpoints expire if the operator stops sending drive
        // commands (key released in the console, cable pulled, app crashed).
        if ((l || r) && commands_ms_since_drive_cmd() > CMD_DEADMAN_MS) {
            drive_stop();
            l = r = 0;
            if (!deadmanStopped) { Serial.println("EVT deadman_stop"); deadmanStopped = true; }
        } else if (l || r) {
            deadmanStopped = false;
        }

        EventBits_t bits = xEventGroupGetBits(gEvents);
        if (bits & EVT_DRIVE_INHIBIT) {          // halt | low-batt | dosing | overtemp
            drive_stop();
        } else if ((bits & EVT_OBSTACLE) && l > 0 && r > 0) {
            drive_stop();                        // block forward only; turning/reverse OK
        } else {
            drive_update();
        }
        vTaskDelay(pdMS_TO_TICKS(DRIVE_LOOP_MS));
    }
}

static void sensorTask(void* pv) {
    sensors_init();
    dosing_init(gEvents);
    bool lowBattAlerted = false, overTempAlerted = false, obstacleAlerted = false;
    uint32_t tick = 0;

    for (;;) {
        sensors_poll_fast();   // ultrasonic @5 Hz - obstacle reaction stays quick
        const Telemetry& t = sensors_snapshot();

        if (t.front_distance_cm > 0 && t.front_distance_cm < US_STOP_DISTANCE_CM) {
            xEventGroupSetBits(gEvents, EVT_OBSTACLE);
            if (!obstacleAlerted) {
                Serial.println("ALERT {\"type\":\"obstacle\"}");
                obstacleAlerted = true;
            }
        } else {
            xEventGroupClearBits(gEvents, EVT_OBSTACLE);
            obstacleAlerted = false;
        }

        if (++tick % SLOW_SENSE_EVERY == 0) {
            sensors_poll_slow();   // NPK, DHT22, moisture, battery @1 Hz

            // Battery cutoff -> latch drive inhibit + one alert (hysteresis).
            if (t.battery_v < LIPO_CUTOFF_V) {
                xEventGroupSetBits(gEvents, EVT_LOW_BATTERY);
                if (!lowBattAlerted) {
                    Serial.println("ALERT {\"type\":\"low_battery\"}");
                    lowBattAlerted = true;
                }
            } else if (t.battery_v > LIPO_CUTOFF_V + 0.3f) {
                xEventGroupClearBits(gEvents, EVT_LOW_BATTERY);
                lowBattAlerted = false;
            }

            // Thermal guardian: ESP32 die temperature (field heat, FC-02).
            if (t.chip_temp_c > ESP32_OVERTEMP_C) {
                xEventGroupSetBits(gEvents, EVT_OVERTEMP);
                if (!overTempAlerted) {
                    Serial.println("ALERT {\"type\":\"overtemp\"}");
                    overTempAlerted = true;
                }
            } else if (t.chip_temp_c < ESP32_OVERTEMP_CLEAR_C) {
                xEventGroupClearBits(gEvents, EVT_OVERTEMP);
                overTempAlerted = false;
            }

            telemetry_print();
        }

        if (xEventGroupGetBits(gEvents) & EVT_DOSE_REQUEST) {
            dosing_run_sequence();   // sets EVT_DOSING internally -> drive halts
            xEventGroupClearBits(gEvents, EVT_DOSE_REQUEST);
        }
        vTaskDelay(pdMS_TO_TICKS(FAST_SENSE_MS));
    }
}

void setup() {
    Serial.begin(LINK_BAUD);
    relaysFailSafeOff();   // FIRST: guarantee pump + actuator are off at boot

    gEvents = xEventGroupCreate();
    commands_init(gEvents);
    telemetry_init(gEvents);

    esp_task_wdt_init(WDT_TIMEOUT_S, true);

    xTaskCreatePinnedToCore(driveTask,  "drive",  TASK_STACK_WORDS, nullptr, 2,
                            nullptr, TASK_DRIVE_CORE);
    xTaskCreatePinnedToCore(sensorTask, "sensor", TASK_STACK_WORDS, nullptr, 1,
                            nullptr, TASK_SENSOR_CORE);

    Serial.println("BOOT agrirover-basic ready (type HELP)");
}

void loop() {
    vTaskDelay(pdMS_TO_TICKS(1000));   // everything runs in FreeRTOS tasks
}
