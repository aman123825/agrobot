/**
 * AgriRover BASIC BOT - ESP32-CAM (AI-Thinker) live video.
 *
 * Brings up the OV2640 and serves:
 *   http://<ip>/         - a tiny HTML page that shows the stream
 *   http://<ip>/stream   - multipart MJPEG stream
 *   http://<ip>/jpg      - a single JPEG snapshot
 *
 * It joins the WiFi access point hosted by the main DevKit and uses static IP
 * 192.168.4.2. A phone joins the same "AgriRover-Control" network and views
 * this stream inside the control page at http://192.168.4.1/.
 *
 * Board: AI-Thinker ESP32-CAM (no USB - flash with a 3.3V FTDI adapter, IO0->GND
 * to enter the bootloader). The camera + PSRAM use most GPIOs; don't reuse them.
 */
#include <Arduino.h>
#include <WiFi.h>
#include "esp_camera.h"
#include "esp_http_server.h"
#include "network_config.h"

#define CAM_JOIN_TIMEOUT_MS 20000UL
#define CAM_RECONNECT_MS     5000UL

// ---- AI-Thinker ESP32-CAM pin map ----
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

static httpd_handle_t sServer = nullptr;

#define PART_BOUNDARY "123456789000000000000987654321"
static const char* STREAM_CONTENT_TYPE =
    "multipart/x-mixed-replace;boundary=" PART_BOUNDARY;
static const char* STREAM_BOUNDARY = "\r\n--" PART_BOUNDARY "\r\n";
static const char* STREAM_PART =
    "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n";

static esp_err_t index_handler(httpd_req_t* req) {
    static const char page[] =
        "<!doctype html><html><head><meta name=viewport "
        "content='width=device-width,initial-scale=1'>"
        "<title>AgriRover CAM</title></head>"
        "<body style='margin:0;background:#111;text-align:center'>"
        "<img src='/stream' style='width:100%;max-width:800px'/>"
        "</body></html>";
    httpd_resp_set_type(req, "text/html");
    return httpd_resp_send(req, page, HTTPD_RESP_USE_STRLEN);
}

static esp_err_t jpg_handler(httpd_req_t* req) {
    camera_fb_t* fb = esp_camera_fb_get();
    if (!fb) { httpd_resp_send_500(req); return ESP_FAIL; }
    httpd_resp_set_type(req, "image/jpeg");
    httpd_resp_set_hdr(req, "Content-Disposition", "inline; filename=capture.jpg");
    esp_err_t res = httpd_resp_send(req, (const char*)fb->buf, fb->len);
    esp_camera_fb_return(fb);
    return res;
}

static esp_err_t stream_handler(httpd_req_t* req) {
    esp_err_t res = httpd_resp_set_type(req, STREAM_CONTENT_TYPE);
    if (res != ESP_OK) return res;
    httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");

    char part[64];
    while (true) {
        camera_fb_t* fb = esp_camera_fb_get();
        if (!fb) { res = ESP_FAIL; break; }

        res = httpd_resp_send_chunk(req, STREAM_BOUNDARY, strlen(STREAM_BOUNDARY));
        if (res == ESP_OK) {
            size_t hlen = snprintf(part, sizeof(part), STREAM_PART, fb->len);
            res = httpd_resp_send_chunk(req, part, hlen);
        }
        if (res == ESP_OK) {
            res = httpd_resp_send_chunk(req, (const char*)fb->buf, fb->len);
        }
        esp_camera_fb_return(fb);
        if (res != ESP_OK) break;   // client disconnected
    }
    return res;
}

static void startServer() {
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.server_port = 80;
    if (httpd_start(&sServer, &config) == ESP_OK) {
        httpd_uri_t index_uri  = { "/",       HTTP_GET, index_handler,  nullptr };
        httpd_uri_t jpg_uri    = { "/jpg",    HTTP_GET, jpg_handler,    nullptr };
        httpd_uri_t stream_uri = { "/stream", HTTP_GET, stream_handler, nullptr };
        httpd_register_uri_handler(sServer, &index_uri);
        httpd_register_uri_handler(sServer, &jpg_uri);
        httpd_register_uri_handler(sServer, &stream_uri);
    }
}

static bool initCamera() {
    camera_config_t c = {};
    c.ledc_channel = LEDC_CHANNEL_0;
    c.ledc_timer   = LEDC_TIMER_0;
    c.pin_d0 = Y2_GPIO_NUM; c.pin_d1 = Y3_GPIO_NUM;
    c.pin_d2 = Y4_GPIO_NUM; c.pin_d3 = Y5_GPIO_NUM;
    c.pin_d4 = Y6_GPIO_NUM; c.pin_d5 = Y7_GPIO_NUM;
    c.pin_d6 = Y8_GPIO_NUM; c.pin_d7 = Y9_GPIO_NUM;
    c.pin_xclk = XCLK_GPIO_NUM; c.pin_pclk = PCLK_GPIO_NUM;
    c.pin_vsync = VSYNC_GPIO_NUM; c.pin_href = HREF_GPIO_NUM;
    // NOTE: field names are pin_sccb_sda/scl on arduino-esp32 2.x. On very old
    // cores rename these to pin_sscb_sda/scl.
    c.pin_sccb_sda = SIOD_GPIO_NUM; c.pin_sccb_scl = SIOC_GPIO_NUM;
    c.pin_pwdn = PWDN_GPIO_NUM; c.pin_reset = RESET_GPIO_NUM;
    c.xclk_freq_hz = 20000000;
    c.pixel_format = PIXFORMAT_JPEG;
    c.frame_size   = FRAMESIZE_VGA;   // 640x480 with PSRAM
    c.jpeg_quality = 12;              // 0-63, lower = better quality / larger
    c.fb_count     = psramFound() ? 2 : 1;
    c.grab_mode    = CAMERA_GRAB_LATEST;
    c.fb_location  = psramFound() ? CAMERA_FB_IN_PSRAM : CAMERA_FB_IN_DRAM;
    if (!psramFound()) c.frame_size = FRAMESIZE_QVGA;   // 320x240 fallback

    esp_err_t err = esp_camera_init(&c);
    if (err != ESP_OK) {
        Serial.printf("camera init failed: 0x%x\n", err);
        return false;
    }
    return true;
}

void setup() {
    Serial.begin(115200);
    Serial.setDebugOutput(false);

    if (!initCamera()) {
        Serial.println("CAM init failed - check the ribbon cable and 5V supply.");
        return;
    }

    WiFi.mode(WIFI_STA);
    WiFi.setAutoReconnect(true);
    WiFi.persistent(false);
    IPAddress ip(ROVER_CAM_IP_A, ROVER_CAM_IP_B, ROVER_CAM_IP_C, ROVER_CAM_IP_D);
    IPAddress gateway(ROVER_AP_IP_A, ROVER_AP_IP_B, ROVER_AP_IP_C, ROVER_AP_IP_D);
    IPAddress subnet(ROVER_NETMASK_A, ROVER_NETMASK_B, ROVER_NETMASK_C, ROVER_NETMASK_D);
    WiFi.config(ip, gateway, subnet, gateway);
    WiFi.begin(ROVER_AP_SSID, ROVER_AP_PASSWORD);
    Serial.printf("Joining rover AP '%s'", ROVER_AP_SSID);
    unsigned long deadline = millis() + CAM_JOIN_TIMEOUT_MS;
    while (WiFi.status() != WL_CONNECTED && millis() < deadline) {
        delay(250);
        Serial.print('.');
    }
    Serial.println();
    if (WiFi.status() == WL_CONNECTED) {
        Serial.printf("CAM ready: %s\n", ROVER_CAMERA_URL);
        startServer();
    } else {
        Serial.println("CAM WiFi join timed out; will keep retrying.");
    }
}

void loop() {
    static unsigned long lastAttempt = 0;
    if (WiFi.status() != WL_CONNECTED && millis() - lastAttempt >= CAM_RECONNECT_MS) {
        lastAttempt = millis();
        Serial.println("CAM WiFi reconnecting...");
        WiFi.disconnect();
        WiFi.begin(ROVER_AP_SSID, ROVER_AP_PASSWORD);
    }
    if (WiFi.status() == WL_CONNECTED && !sServer) {
        Serial.printf("CAM reconnected: %s\n", ROVER_CAMERA_URL);
        startServer();
    }
    delay(250);
}
