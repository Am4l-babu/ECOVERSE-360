"""
ECOVERSE 360 — MQTT IoT Data Ingestion Service
Subscribes to MQTT topics and stores sensor data in PostgreSQL.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Optional

import paho.mqtt.client as mqtt

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger("ecoverse.mqtt")

# ── MQTT Topic Structure ────────────────────────────────────────────────
# ecoverse/sensors/{device_id}/data     → sensor readings
# ecoverse/sensors/{device_id}/status   → device heartbeat
# ecoverse/bins/{bin_code}/update       → bin level updates
# ecoverse/farm/{plot_id}/data          → farm sensor data
# ecoverse/energy/tiles/{tile_id}       → energy harvesting data

TOPICS = [
    ("ecoverse/sensors/+/data", 1),
    ("ecoverse/sensors/+/status", 0),
    ("ecoverse/bins/+/update", 1),
    ("ecoverse/farm/+/data", 1),
    ("ecoverse/energy/tiles/+", 0),
]


class MQTTService:
    """
    MQTT client for IoT device communication.

    Subscribes to sensor topics and forwards data to the database
    via the REST API or directly via SQLAlchemy.
    """

    def __init__(self):
        self.client = mqtt.Client(
            client_id="ecoverse-backend",
            protocol=mqtt.MQTTv311,
        )
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect

        if settings.MQTT_USERNAME:
            self.client.username_pw_set(
                settings.MQTT_USERNAME, settings.MQTT_PASSWORD
            )

        self._message_handlers = {
            "sensors": self._handle_sensor_data,
            "bins": self._handle_bin_update,
            "farm": self._handle_farm_data,
            "energy": self._handle_energy_data,
        }

    def start(self):
        """Connect to MQTT broker and start listening."""
        try:
            self.client.connect(
                settings.MQTT_BROKER_HOST,
                settings.MQTT_BROKER_PORT,
                keepalive=60,
            )
            self.client.loop_start()
            logger.info(
                f"MQTT connected to {settings.MQTT_BROKER_HOST}:{settings.MQTT_BROKER_PORT}"
            )
        except Exception as e:
            logger.error(f"MQTT connection failed: {e}")

    def stop(self):
        """Disconnect from MQTT broker."""
        self.client.loop_stop()
        self.client.disconnect()
        logger.info("MQTT disconnected")

    def publish(self, topic: str, payload: dict, qos: int = 1):
        """Publish a message to an MQTT topic."""
        self.client.publish(topic, json.dumps(payload), qos=qos)

    # ── Callbacks ────────────────────────────────────────────────────

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("MQTT connected successfully")
            for topic, qos in TOPICS:
                client.subscribe(topic, qos)
                logger.info(f"Subscribed to {topic}")
        else:
            logger.error(f"MQTT connection failed with code {rc}")

    def _on_disconnect(self, client, userdata, rc):
        if rc != 0:
            logger.warning(f"MQTT unexpected disconnect (rc={rc}), reconnecting...")

    def _on_message(self, client, userdata, msg):
        """Route incoming messages to appropriate handlers."""
        try:
            topic_parts = msg.topic.split("/")
            if len(topic_parts) < 3:
                return

            category = topic_parts[1]  # sensors, bins, farm, energy
            payload = json.loads(msg.payload.decode())

            handler = self._message_handlers.get(category)
            if handler:
                handler(topic_parts, payload)
            else:
                logger.warning(f"No handler for category: {category}")

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON on topic {msg.topic}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    # ── Message Handlers ─────────────────────────────────────────────

    def _handle_sensor_data(self, topic_parts: list, payload: dict):
        """
        Handle sensor data messages.
        Expected payload: {"value": 42.5, "unit": "ppm", "quality": 0.95}
        """
        device_id = topic_parts[2]
        logger.info(
            f"Sensor data from {device_id}: "
            f"{payload.get('value')} {payload.get('unit', '')}"
        )
        # In production: write to database via async task
        # For now: log and forward to REST API
        self._forward_to_api(
            "/api/v1/sensors/data",
            {
                "device_id": device_id,
                "value": payload.get("value"),
                "unit": payload.get("unit", "raw"),
                "quality": payload.get("quality", 1.0),
                "metadata": payload.get("metadata", {}),
            },
        )

    def _handle_bin_update(self, topic_parts: list, payload: dict):
        """
        Handle smart bin level updates.
        Expected payload: {"level": 75.5, "weight": 8.3}
        """
        bin_code = topic_parts[2]
        logger.info(
            f"Bin update {bin_code}: level={payload.get('level')}% "
            f"weight={payload.get('weight')}kg"
        )

    def _handle_farm_data(self, topic_parts: list, payload: dict):
        """
        Handle vertical farm sensor data.
        Expected payload: {"soil_moisture": 65, "temp": 28, "humidity": 70, ...}
        """
        plot_id = topic_parts[2]
        logger.info(f"Farm data from plot {plot_id}: {payload}")

    def _handle_energy_data(self, topic_parts: list, payload: dict):
        """
        Handle energy harvesting tile data.
        Expected payload: {"watts": 0.5, "steps": 150}
        """
        tile_id = topic_parts[3] if len(topic_parts) > 3 else "unknown"
        logger.info(
            f"Energy tile {tile_id}: {payload.get('watts', 0)}W "
            f"({payload.get('steps', 0)} steps)"
        )

    def _forward_to_api(self, endpoint: str, data: dict):
        """Forward processed data to REST API (async in production)."""
        # This would use httpx in production:
        # async with httpx.AsyncClient() as client:
        #     await client.post(f"http://localhost:8000{endpoint}", json=data)
        logger.debug(f"Forward to {endpoint}: {data}")


# ── Singleton ────────────────────────────────────────────────────────────
mqtt_service = MQTTService()
