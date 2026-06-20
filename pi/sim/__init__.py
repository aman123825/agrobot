"""Simulation harness for the AgroBot rover.

Emulates the ESP32 serial link and sensor telemetry so the Pi orchestrator,
navigation, and PID modules can be tested without physical hardware.

Modules:
    rover_model  - Differential-drive kinematic model
    sensor_sim   - Synthetic telemetry matching real MQTT payloads
    serial_sim   - Drop-in replacement for serial.Serial (HMAC-verified)
    run_sim      - Standalone simulation runner
"""
