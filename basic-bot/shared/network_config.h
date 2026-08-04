#pragma once

// Shared by the DevKit control firmware and the separate ESP32-CAM firmware.
// Change the password before field use; WPA2 requires at least 8 characters.
#define ROVER_AP_SSID        "AgriRover-Control"
#define ROVER_AP_PASSWORD    "agrirover123"
#define ROVER_AP_CHANNEL     6
#define ROVER_AP_MAX_CLIENTS 4

#define ROVER_AP_IP_A        192
#define ROVER_AP_IP_B        168
#define ROVER_AP_IP_C        4
#define ROVER_AP_IP_D        1

#define ROVER_CAM_IP_A       192
#define ROVER_CAM_IP_B       168
#define ROVER_CAM_IP_C       4
#define ROVER_CAM_IP_D       2

#define ROVER_NETMASK_A      255
#define ROVER_NETMASK_B      255
#define ROVER_NETMASK_C      255
#define ROVER_NETMASK_D      0

#define ROVER_CONTROL_URL    "http://192.168.4.1/"
#define ROVER_CAMERA_URL     "http://192.168.4.2/"
#define ROVER_CAMERA_STREAM  "http://192.168.4.2/stream"
