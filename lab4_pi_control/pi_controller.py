"""
Lab 4: Proportional-Integral (PI) Controller
Slide Reference (Pages 26-27):
- Error = Target - Input
- Actuator = Kp * Error + Ki * sum(Error * dt)
- Eliminates steady-state error caused by constant disturbances / outflows
"""
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.tank_model import WaterTankSimulation

class PIController:
    def __init__(self, kp=0.05, ki=0.01, target_level=50.0):
        self.kp = float(kp)
        self.ki = float(ki)
        self.target_level = float(target_level)
        self.integral = 0.0

    def set_target(self, target):
        self.target_level = float(target)

    def reset(self):
        self.integral = 0.0

    def update(self, current_level, dt=0.5):
        """
        Calculate valve output using PI control:
        P_term = Kp * Error
        I_term = Ki * sum(Error * dt)
        """
        error = self.target_level - current_level
        self.integral += error * dt
        
        # Anti-windup clamp for integral term
        self.integral = max(-100.0, min(100.0, self.integral))

        output = (self.kp * error) + (self.ki * self.integral)
        valve_pos = max(0.0, min(1.0, output))
        return valve_pos, error

def run_lab4_pi_control(kp=0.05, ki=0.01, target=50.0, outflow=0.3, duration=80.0, dt=0.5):
    print("=" * 60)
    print("Lab 4: Proportional-Integral (PI) Control")
    print(f"Kp: {kp} | Ki: {ki} | Target: {target} m | Outflow: {outflow} m^3/s")
    
    tank = WaterTankSimulation(initial_level=20.0)
    tank.c = (1.0 * tank.rho * tank.area) / 100.0
    tank.set_outflow(outflow)
    controller = PIController(kp=kp, ki=ki, target_level=target)

    t = 0.0
    while t <= duration:
        level = tank.get_level()
        valve, err = controller.update(level, dt=dt)
        tank.set_valve_in(valve)
        tank.step(dt)
        if int(t * 10) % 20 == 0:
            print(f"Time: {t:4.1f}s | Level: {level:6.2f} m | Error: {err:6.2f} | Valve: {valve*100:5.1f}%")
        t += dt
    print("=" * 60)

if __name__ == "__main__":
    run_lab4_pi_control(kp=0.05, ki=0.01, target=50.0, outflow=0.3, duration=60.0)
