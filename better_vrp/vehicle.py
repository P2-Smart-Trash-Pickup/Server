class Vehicle:
    def __init__(
        self,
        max_capacity: float,
        max_volume,
        battery_capacity: float,
        acceleration: float,
        time_constraint: float,
        initial_mass: float,
    ) -> None:
        self.max_volume = max_volume
        self.current_volume = 0.0
        self.max_capacity = max_capacity
        self.battery_capacity = battery_capacity
        self.acceleration = acceleration
        self.time_constraint = time_constraint
        self.initial_mass = initial_mass
