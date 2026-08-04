"""Thin paho-mqtt wrapper for subscribing to rover telemetry and publishing
alerts (BOM #108). The ESP32 publishes; the Pi subscribes and routes to
Pathway + the dashboard.

paho is imported lazily so modules that *reference* MqttClient still import on
a machine without it; constructing MqttClient without paho raises.
"""
from __future__ import annotations

from collections.abc import Callable

import config


class MqttClient:
    def __init__(self, host: str = config.MQTT_HOST, port: int = config.MQTT_PORT):
        import paho.mqtt.client as mqtt

        self.host = host
        self.port = port
        self._client = mqtt.Client()
        self._handlers: dict[str, Callable[[str], None]] = {}
        self._client.on_message = self._on_message

        # Authentication + optional TLS (hardening).
        if config.MQTT_USERNAME:
            self._client.username_pw_set(config.MQTT_USERNAME, config.MQTT_PASSWORD)
        if config.MQTT_TLS:
            self._client.tls_set(ca_certs=config.MQTT_CA_CERT or None)

    def connect(self) -> None:
        self._client.connect(self.host, self.port)

    def subscribe(self, topic: str, handler: Callable[[str], None]) -> None:
        self._handlers[topic] = handler
        self._client.subscribe(topic)

    def publish(self, topic: str, payload: str) -> None:
        self._client.publish(topic, payload)

    def _on_message(self, _client, _userdata, msg) -> None:
        handler = self._handlers.get(msg.topic)
        if handler:
            handler(msg.payload.decode(errors="ignore"))

    def loop_forever(self) -> None:
        self._client.loop_forever()
