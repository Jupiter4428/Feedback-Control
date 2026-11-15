"""
Tank Simulation with MQTT & ThingsBoard Support
Slide 12-14:
- Publishes sensor data to Thingsboard telemetry topic (v1/devices/me/telemetry)
- Publishes/Subscribes to Node-Red topics via MQTT
- Supports switching controllers (Open Loop, ON/OFF, P, PI)
"""
import json
import time
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None
from models.tank_model import WaterTankSimulation
from lab2_on_off.on_off_controller import OnOffController
from lab3_p_control.p_controller import PController
from lab4_pi_control.pi_controller import PIController

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
THINGSBOARD_TOKEN = os.getenv("THINGSBOARD_TOKEN", "tank_device_token")

# Topics
TOPIC_TELEMETRY = "v1/devices/me/telemetry"             # ThingsBoard standard telemetry
TOPIC_SET_TARGET = "tank/control/target"                # Target water level (m)
TOPIC_SET_VALVE = "tank/control/valve"                  # Manual valve command (0-100%)
TOPIC_SET_MODE = "tank/control/mode"                    # Mode: manual, on_off, p, pi
TOPIC_SET_OUTFLOW = "tank/control/outflow"              # Outflow rate (m^3/s)

class TankMQTTService:
    def __init__(self):
        self.tank = WaterTankSimulation(initial_level=0.0)
        self.mode = "on_off" # manual, on_off, p, pi
        self.target = 50.0
        
        self.on_off_ctrl = OnOffController(target_level=self.target)
        self.p_ctrl = PController(kp=0.05, target_level=self.target)
        self.pi_ctrl = PIController(kp=0.05, ki=0.01, target_level=self.target)

        self.client = mqtt.Client(client_id="tank_simulator")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected to MQTT Broker with result code {rc}")
        client.subscribe([(TOPIC_SET_TARGET, 0), (TOPIC_SET_VALVE, 0), 
                          (TOPIC_SET_MODE, 0), (TOPIC_SET_OUTFLOW, 0)])

    def on_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode()
            if msg.topic == TOPIC_SET_TARGET:
                val = float(payload)
                self.target = val
                self.on_off_ctrl.set_target(val)
                self.p_ctrl.set_target(val)
                self.pi_ctrl.set_target(val)
                print(f"[MQTT] Updated Target Level: {val} m")
            elif msg.topic == TOPIC_SET_VALVE:
                val = float(payload)
                self.tank.set_valve_in(val)
                print(f"[MQTT] Manual Valve Set: {val}%")
            elif msg.topic == TOPIC_SET_MODE:
                self.mode = payload.strip().lower()
                print(f"[MQTT] Controller Mode Changed to: {self.mode}")
            elif msg.topic == TOPIC_SET_OUTFLOW:
                val = float(payload)
                self.tank.set_outflow(val)
                print(f"[MQTT] Outflow Rate Set to: {val} m^3/s")
        except Exception as e:
            print(f"Error handling message: {e}")

    def run(self, dt=0.5):
        try:
            self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.client.loop_start()
        except Exception as e:
            print(f"MQTT connection failed ({e}). Running in standalone simulation mode...")

        print("Tank simulation running. Press Ctrl+C to stop.")
        try:
            while True:
                level = self.tank.get_level()
                
                # Controller compute based on mode
                if self.mode == "on_off":
                    valve = self.on_off_ctrl.update(level)
                    self.tank.set_valve_in(valve)
                elif self.mode == "p":
                    valve, _ = self.p_ctrl.update(level)
                    self.tank.set_valve_in(valve)
                elif self.mode == "pi":
                    valve, _ = self.pi_ctrl.update(level, dt=dt)
                    self.tank.set_valve_in(valve)
                
                # Step physics
                self.tank.step(dt)

                # Telemetry payload matching Thingsboard slide 13
                # {"water_sensor_depth": 43.3, "water_sensor_limit_switch": 1, "valve_position": 100}
                payload = {
                    "water_sensor_depth": round(self.tank.get_level(), 3),
                    "water_sensor_limit_switch": 1 if self.tank.get_digital_sensor(self.target) else 0,
                    "valve_position": round(self.tank.valve_in * 100, 2),
                    "target_level": self.target,
                    "mode": self.mode
                }
                
                # Publish to ThingsBoard / MQTT
                if self.client.is_connected():
                    self.client.publish(TOPIC_TELEMETRY, json.dumps(payload))
                
                print(f"[STATUS] Mode: {self.mode.upper():6} | Level: {payload['water_sensor_depth']:6.2f}m | Target: {self.target}m | Valve: {payload['valve_position']:5.1f}%")
                time.sleep(dt)
        except KeyboardInterrupt:
            print("\nStopping simulation.")
        finally:
            self.client.loop_stop()

if __name__ == "__main__":
    service = TankMQTTService()
    service.run()
