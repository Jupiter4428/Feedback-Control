"""
Lab 2: Closed-Loop ON/OFF Control with Hysteresis (Threshold +-10%)
Slide Reference (Pages 17-22):
- Prevents rapid chatter / oscillation around target level
- Threshold upper limit = Target * (1 + threshold_pct)
- Threshold lower limit = Target * (1 - threshold_pct)
- Outflow rate is controllable and less than max inflow rate
"""
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.tank_model import WaterTankSimulation

class OnOffController:
    def __init__(self, target_level=50.0, threshold_pct=0.10):
        self.target_level = float(target_level)
        self.threshold_pct = float(threshold_pct)
        self.upper_threshold = self.target_level * (1.0 + self.threshold_pct)
        self.lower_threshold = self.target_level * (1.0 - self.threshold_pct)
        self.valve_state = 0.0 # 0.0 (OFF) or 1.0 (ON)

    def set_target(self, target):
        self.target_level = float(target)
        self.upper_threshold = self.target_level * (1.0 + self.threshold_pct)
        self.lower_threshold = self.target_level * (1.0 - self.threshold_pct)

    def update(self, current_level):
        """
        Hysteresis ON/OFF logic:
        - If level falls below lower_threshold: Turn ON valve
        - If level rises above upper_threshold: Turn OFF valve
        - If in between: retain previous valve state
        """
        if current_level <= self.lower_threshold:
            self.valve_state = 1.0
        elif current_level >= self.upper_threshold:
            self.valve_state = 0.0
        return self.valve_state

def run_lab2_on_off(target=50.0, outflow=0.3, duration=60.0, dt=0.5):
    print("=" * 60)
    print("Lab 2: ON/OFF Control with Hysteresis (+-10%)")
    tank = WaterTankSimulation(initial_level=20.0)
    # Set max inflow to 1.0 m/s
    tank.c = (1.0 * tank.rho * tank.area) / 100.0
    tank.set_outflow(outflow)
    
    controller = OnOffController(target_level=target, threshold_pct=0.10)
    print(f"Target Level:    {controller.target_level:.2f} m")
    print(f"Lower Threshold: {controller.lower_threshold:.2f} m (-10%)")
    print(f"Upper Threshold: {controller.upper_threshold:.2f} m (+10%)")
    print(f"Outflow Rate:    {outflow} m^3/s (Max Inflow = 1.0 m^3/s)")
    print("-" * 60)

    t = 0.0
    while t <= duration:
        level = tank.get_level()
        valve = controller.update(level)
        tank.set_valve_in(valve)
        tank.step(dt)
        state_str = "ON (100%)" if valve > 0 else "OFF (0%) "
        if int(t * 10) % 20 == 0:  # print every 2 seconds
            print(f"Time: {t:4.1f}s | Level: {level:6.2f} m | Valve: {state_str}")
        t += dt
    print("=" * 60)

if __name__ == "__main__":
    run_lab2_on_off(target=50.0, outflow=0.3, duration=40.0)
