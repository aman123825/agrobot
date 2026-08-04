#include <Arduino.h>
#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include "../include/config.h"
#include "../../shared/network_config.h"
#include "command_dispatch.h"
#include "mobile_page.h"
#include "mobile_server.h"

static AsyncWebServer sServer(80);
static AsyncWebSocket sSocket("/ws");
static bool sStarted = false;

static void wsReply(void* user, const char* line) {
    AsyncWebSocketClient* client = static_cast<AsyncWebSocketClient*>(user);
    if (client && client->status() == WS_CONNECTED) client->text(line);
}

static void sendHello(AsyncWebSocketClient* client) {
    char hello[180];
    snprintf(hello, sizeof(hello),
             "{\"t\":\"hello\",\"cam\":\"%s\",\"deadman_ms\":%u}",
             ROVER_CAMERA_STREAM, CMD_DEADMAN_MS);
    client->text(hello);
}

static void onWsEvent(AsyncWebSocket* server, AsyncWebSocketClient* client,
                      AwsEventType type, void* arg, uint8_t* data, size_t len) {
    (void)server;
    if (type == WS_EVT_CONNECT) {
        sendHello(client);
        return;
    }
    if (type == WS_EVT_DISCONNECT) {
        control_stop_if_owner({ControlSource::WEBSOCKET, client->id()});
        return;
    }
    if (type != WS_EVT_DATA) return;

    AwsFrameInfo* info = static_cast<AwsFrameInfo*>(arg);
    if (!info || info->opcode != WS_TEXT || info->index != 0 ||
        info->len != len || len >= 96) {
        client->text("NAK frame");
        return;
    }
    char command[96];
    memcpy(command, data, len);
    command[len] = '\0';
    // The browser uses the same line grammar as the USB console.
    const CommandContext ctx = {{ControlSource::WEBSOCKET, client->id()}, wsReply, client};
    command_dispatch(ctx, command);
}

void mobile_server_start() {
    if (sStarted) return;
    WiFi.mode(WIFI_AP);
    IPAddress ip(ROVER_AP_IP_A, ROVER_AP_IP_B, ROVER_AP_IP_C, ROVER_AP_IP_D);
    IPAddress mask(ROVER_NETMASK_A, ROVER_NETMASK_B, ROVER_NETMASK_C, ROVER_NETMASK_D);
    WiFi.softAPConfig(ip, ip, mask);
    WiFi.softAP(ROVER_AP_SSID, ROVER_AP_PASSWORD, ROVER_AP_CHANNEL,
                false, ROVER_AP_MAX_CLIENTS);

    sSocket.onEvent(onWsEvent);
    sServer.addHandler(&sSocket);
    sServer.on("/", HTTP_GET, [](AsyncWebServerRequest* request) {
        request->send(200, "text/html", MOBILE_PAGE);
    });
    sServer.on("/version", HTTP_GET, [](AsyncWebServerRequest* request) {
        char body[128];
        snprintf(body, sizeof(body), "{\"fw\":\"basic-mobile-1\",\"uptime\":%lu,\"clients\":%u}",
                 (unsigned long)millis(), WiFi.softAPgetStationNum());
        request->send(200, "application/json", body);
    });
    sServer.begin();
    sStarted = true;
    Serial.printf("AP %s @ %s, ch %d, clients=0/%d\n", ROVER_AP_SSID,
                  WiFi.softAPIP().toString().c_str(), ROVER_AP_CHANNEL,
                  ROVER_AP_MAX_CLIENTS);
}

void mobile_server_poll() {
    if (sStarted) sSocket.cleanupClients();
}

void mobile_server_broadcast_line(const char* line) {
    if (sStarted && line) sSocket.textAll(line);
}
