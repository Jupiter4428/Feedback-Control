"""
Interactive Presentation & Demo Script for ThingsBoard Cloud
Scenario runner that dynamically changes controller modes, targets, and disturbances.
"""
import json
import time
import os
import sys
import threading
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import paho.mqtt.client as mqtt
from models.tank_model import WaterTankSimulation
from lab2_on_off.on_off_controller import OnOffController
from lab3_p_control.p_controller import PController
from lab4_pi_control.pi_controller import PIController

MQTT_BROKER = os.getenv("MQTT_BROKER", "thingsboard.cloud")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
THINGSBOARD_TOKEN = os.getenv("THINGSBOARD_TOKEN", "Gv7jGS7fQLKUFREjxgTf")
TOPIC_TELEMETRY = "v1/devices/me/telemetry"

class PresentationDemo:
    def __init__(self):
        self.tank = WaterTankSimulation(initial_level=10.0)
        self.running = False
        self.mode = "on_off" # "open_loop", "on_off", "p", "pi"
        self.target = 50.0
        self.scenario_name = "Lab 2: ON/OFF Control (Hysteresis)"
        
        self.on_off_ctrl = OnOffController(target_level=self.target)
        self.p_ctrl = PController(kp=0.05, target_level=self.target)
        self.pi_ctrl = PIController(kp=0.05, ki=0.015, target_level=self.target)
        
        # Open loop state
        self.open_loop_start = None
        self.open_loop_duration = 0.0

        try:
            self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="tank_demo_presenter")
        except AttributeError:
            self.client = mqtt.Client(client_id="tank_demo_presenter")
        if THINGSBOARD_TOKEN:
            self.client.username_pw_set(THINGSBOARD_TOKEN)

    def clear(self):
        self.running = False
        self.tank = WaterTankSimulation(initial_level=10.0)
        self.target = 50.0
        self.on_off_ctrl = OnOffController(target_level=self.target)
        self.p_ctrl = PController(kp=0.05, target_level=self.target)
        self.pi_ctrl = PIController(kp=0.05, ki=0.015, target_level=self.target)
        self.open_loop_start = None
        self.open_loop_duration = 0.0
        self.scenario_name = "Cleared / Idle"
        payload = {
            "water_sensor_depth": round(self.tank.get_level(), 2),
            "water_sensor_limit_switch": 0,
            "valve_position": 0.0,
            "target_level": self.target,
            "operating_mode": self.scenario_name,
            "mode": "idle"
        }
        if self.client.is_connected():
            self.client.publish(TOPIC_TELEMETRY, json.dumps(payload))
        print("\n[CLEARED] Simulation stopped and state reset to initial level (10.0m).")

    def set_scenario(self, scenario_id):
        current_level = self.tank.get_level()
        self.running = True
        if scenario_id == "1":
            # Scenario 1: Open Loop (ต่อเนื่องจากระดับน้ำปัจจุบัน)
            self.mode = "open_loop"
            self.target = 60.0
            self.tank.set_outflow(0.0)
            fill_rate = (self.tank.c / (self.tank.rho * self.tank.area)) * 100.0
            self.open_loop_duration = max(0.0, (self.target - current_level) / fill_rate)
            self.open_loop_start = time.time()
            self.scenario_name = f"1. Open Loop (From {current_level:.1f}m -> {self.target}m)"
            print(f"\n[SCENARIO 1 STARTED] Open Loop | Current: {current_level:.1f}m -> Target: {self.target}m | Duration: {self.open_loop_duration:.1f}s")

        elif scenario_id == "2":
            # Scenario 2: ON/OFF with Hysteresis
            self.mode = "on_off"
            self.target = 50.0
            self.on_off_ctrl.set_target(50.0)
            self.tank.set_outflow(0.15) # มีน้ำไหลออกเพื่อให้เห็นการตัดต่อ
            self.scenario_name = "2. ON/OFF Control (+-10% Hysteresis)"
            print(f"\n[SCENARIO 2 STARTED] ON/OFF Control | Target: 50m (+-10%) | Outflow: 0.15 m^3/s")

        elif scenario_id == "3":
            # Scenario 3: P-Control with Disturbance / Offset
            self.mode = "p"
            self.target = 50.0
            self.p_ctrl.set_target(50.0)
            self.tank.set_outflow(0.20) # Outflow สร้าง Steady-State Error
            self.scenario_name = "3. P-Control (Shows Steady-State Error)"
            print(f"\n[SCENARIO 3 STARTED] P Controller | Target: 50m | Demonstrating Steady-State Offset")

        elif scenario_id == "4":
            # Scenario 4: PI-Control Eliminates Offset
            self.mode = "pi"
            self.target = 50.0
            self.pi_ctrl.set_target(50.0)
            self.tank.set_outflow(0.20)
            self.scenario_name = "4. PI-Control (Eliminating Offset to 100%)"
            print(f"\n[SCENARIO 4 STARTED] PI Controller | Target: 50m | Integral Term Active")

    def run(self):
        try:
            self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.client.loop_start()
            print("Connected to ThingsBoard Cloud successfully!")
        except Exception as e:
            print(f"Error connecting: {e}")
            return

        dt = 0.5
        while True:
            if not self.running:
                time.sleep(dt)
                continue

            level = self.tank.get_level()
            
            if self.mode == "open_loop":
                elapsed = time.time() - self.open_loop_start
                if elapsed < self.open_loop_duration:
                    valve = 100.0
                else:
                    valve = 0.0
                self.tank.set_valve_in(valve)
            elif self.mode == "on_off":
                valve = self.on_off_ctrl.update(level)
                self.tank.set_valve_in(valve)
            elif self.mode == "p":
                valve, _ = self.p_ctrl.update(level)
                self.tank.set_valve_in(valve)
            elif self.mode == "pi":
                valve, _ = self.pi_ctrl.update(level, dt=dt)
                self.tank.set_valve_in(valve)

            self.tank.step(dt)

            # Publish to ThingsBoard
            payload = {
                "water_sensor_depth": round(self.tank.get_level(), 2),
                "water_sensor_limit_switch": 1 if self.tank.get_digital_sensor(self.target) else 0,
                "valve_position": round(self.tank.valve_in * 100, 1),
                "target_level": self.target,
                "operating_mode": self.scenario_name,
                "mode": self.mode
            }
            if self.client.is_connected():
                self.client.publish(TOPIC_TELEMETRY, json.dumps(payload))

            time.sleep(dt)

def menu_loop(demo):
    time.sleep(1)
    while True:
        print("\n" + "="*50)
        print("  SELECT SCENARIO TO DEMO ON THINGSBOARD:")
        print("="*50)
        print(" [1] Lab 1: Open Loop (เปิดวาล์วตามเวลาแล้วตัด)")
        print(" [2] Lab 2: ON/OFF Control (เห็นระดับน้ำแกว่ง +-10%)")
        print(" [3] Lab 3: P Control (เห็นระดับน้ำค้าง ไม่ถึงเป้าเพราะมีน้ำรั่ว)")
        print(" [4] Lab 4: PI Control (Integral ค่อยๆ ดันน้ำจนแตะ 50m เป๊ะ)")
        print(" [c] Clear (หยุดและรีเซ็ตสถานะ)")
        print(" [q] Exit")
        print("="*50)
        choice = input("Enter Choice (1-4, c, q): ").strip()
        if choice in ["1", "2", "3", "4"]:
            demo.set_scenario(choice)
        elif choice.lower() == "c":
            demo.clear()
        elif choice.lower() == "q":
            os._exit(0)

if __name__ == "__main__":
    demo = PresentationDemo()
    t = threading.Thread(target=demo.run, daemon=True)
    t.start()
    menu_loop(demo)
