"""
Lab 3: Proportional (P) Controller
Slide Reference (Pages 23-25):
- Error = Target - Input
- Actuator = Kp * Error
- Continuous valve control (0% to 100% or 0.0 to 1.0)
"""
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.tank_model import WaterTankSimulation

class PController:
    def __init__(self, kp=0.05, target_level=50.0):
        self.kp = float(kp)
        self.target_level = float(target_level)

    def set_target(self, target):
        self.target_level = float(target)

    def update(self, current_level):
        """
        Calculate valve output based on error:
        Error = Target - current_level
        Valve = clamp(Kp * Error, 0.0, 1.0)
        """
        error = self.target_level - current_level
        output = self.kp * error
        # Clamp valve output to [0.0, 1.0]
        valve_pos = max(0.0, min(1.0, output))
        return valve_pos, error

def run_lab3_p_control(kp=0.05, target=50.0, outflow=0.3, duration=60.0, dt=0.5):
    print("=" * 60)
    print("Lab 3: Proportional (P) Control")
    print(f"Kp: {kp} | Target: {target} m | Outflow: {outflow} m^3/s")
    
    tank = WaterTankSimulation(initial_level=20.0)
    tank.c = (1.0 * tank.rho * tank.area) / 100.0  # max inflow 1.0 m/s
    tank.set_outflow(outflow)
    controller = PController(kp=kp, target_level=target)

    t = 0.0
    while t <= duration:
        level = tank.get_level()
        valve, err = controller.update(level)
        tank.set_valve_in(valve)
        tank.step(dt)
        if int(t * 10) % 20 == 0:
            print(f"Time: {t:4.1f}s | Level: {level:6.2f} m | Error: {err:6.2f} | Valve: {valve*100:5.1f}%")
        t += dt
    print(f"Note: Notice steady-state error due to constant outflow in pure P control.")
    print("=" * 60)

if __name__ == "__main__":
    run_lab3_p_control(kp=0.05, target=50.0, outflow=0.3, duration=50.0)
