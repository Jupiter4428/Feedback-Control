"""
Water Tank Physical Simulation Model
Based on slide equations:
  (dh/dt) * A = c * u_in - outflow
Where:
  rho = 1000.0 kg/m^3 (water density)
  A = 1.0 m^2 (tank cross-sectional area)
  c = 50.0 (valve coefficient kg/s / %open or m^3/s scale)
  valve = 0.0 to 1.0 (or 0-100%)
  outflow = constant or controllable outflow rate
"""
import time
import math

class WaterTankSimulation:
    def __init__(self, area=1.0, rho=1000.0, c=50.0, initial_level=0.0, max_level=100.0):
        self.area = float(area)         # m^2
        self.rho = float(rho)           # kg/m^3
        self.c = float(c)               # Valve coefficient
        self.level = float(initial_level) # current water level in meters
        self.max_level = float(max_level)
        self.valve_in = 0.0             # 0.0 to 1.0 (0% to 100%)
        self.outflow_rate = 0.0         # m^3/s

    def set_valve_in(self, valve_pos):
        """Set inlet valve position between 0.0 and 1.0 (or clamp if given 0-100)"""
        if valve_pos > 1.0:
            valve_pos = valve_pos / 100.0
        self.valve_in = max(0.0, min(1.0, valve_pos))

    def set_outflow(self, outflow):
        """Set water outflow rate (m^3/s)"""
        self.outflow_rate = max(0.0, outflow)

    def set_level(self, level):
        """Set water level directly (useful for resetting scenarios)"""
        self.level = max(0.0, min(self.max_level, float(level)))

    def step(self, dt=0.1):
        """
        Simulate dynamic step over dt seconds:
        dLevel_dt = (inflow - outflow) / area
        inflow = (c / (rho * A)) * valve_in (scaled as in course slide: c * valve / A)
        Using slide formula:
          dLevel_dt = (self.c / (self.rho * self.area)) * (self.valve_in * 100.0) - (self.outflow_rate / self.area)
        """
        # (c / rho*A) * (% open)
        inflow_velocity = (self.c / (self.rho * self.area)) * (self.valve_in * 100.0)
        outflow_velocity = (self.outflow_rate / self.area) if self.level > 0 else 0.0

        # Change in level
        dh = (inflow_velocity - outflow_velocity) * dt
        self.level = max(0.0, min(self.max_level, self.level + dh))
        return self.level

    def get_digital_sensor(self, threshold):
        """Returns True if level >= threshold (digital limit switch)"""
        return self.level >= threshold

    def get_level(self):
        """Returns analog level in meters"""
        return self.level
