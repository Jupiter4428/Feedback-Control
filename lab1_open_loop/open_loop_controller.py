"""
Lab 1: Open Loop Control (Timer-based)
Slide Reference (Pages 15-16):
- Initial level: 20 m
- Target level: 80 m
- Fill rate: 1 m/s (or calculated from valve max rate)
- Formula: T = (target - initial) / rate
- Operation:
    digital(HIGH)  # open valve
    sleep(T)
    digital(LOW)   # close valve
"""
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.tank_model import WaterTankSimulation

def run_lab1_open_loop(initial_level=20.0, target_level=80.0, max_rate=1.0, simulate_realtime=False):
    print("=" * 50)
    print("Lab 1: Open Loop Control")
    print(f"Initial Level: {initial_level} m")
    print(f"Target Level:  {target_level} m")
    
    delta_h = target_level - initial_level
    if delta_h <= 0:
        print("Target is less than or equal to current level. No filling needed.")
        return

    # Calculate duration T
    T = delta_h / max_rate
    print(f"Calculated Open Duration T = {T:.2f} seconds (at fill rate = {max_rate} m/s)")
    
    # Initialize tank
    tank = WaterTankSimulation(initial_level=initial_level)
    # Calibrate tank parameters to match max_rate at 100% valve
    # inflow_velocity = (c / (rho * A)) * 100 = max_rate -> c = max_rate * rho * A / 100
    tank.c = (max_rate * tank.rho * tank.area) / 100.0

    print("\n--- Starting Open-Loop Action ---")
    print("digital(HIGH) -> Valve OPEN 100%")
    tank.set_valve_in(1.0)
    
    dt = 0.5
    elapsed = 0.0
    while elapsed < T:
        step_dt = min(dt, T - elapsed)
        tank.step(step_dt)
        elapsed += step_dt
        print(f"Time: {elapsed:5.1f}s | Water Level: {tank.get_level():6.2f} m")
        if simulate_realtime:
            time.sleep(step_dt)

    print("sleep(T) completed.")
    print("digital(LOW)  -> Valve CLOSED 0%")
    tank.set_valve_in(0.0)
    print(f"Final Water Level: {tank.get_level():.2f} m (Target was: {target_level} m)")
    print("=" * 50)

if __name__ == "__main__":
    run_lab1_open_loop(initial_level=20.0, target_level=80.0, max_rate=1.0)
