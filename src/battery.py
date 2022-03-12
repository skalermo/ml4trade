from src.custom_types import kWh


class Battery:
    def __init__(self, capacity: kWh = kWh(100), efficiency: float = 1.0, current_charge: kWh = kWh(0)):
        assert efficiency > 0, "Efficiency must be greater than 0"

        self.capacity = capacity
        self.efficiency = efficiency
        self.current_charge = current_charge

    def charge(self, amount: kWh):
        charged_amount = min(amount * self.efficiency, self.capacity - self.current_charge)
        self.current_charge += charged_amount
        return charged_amount / self.efficiency

    def discharge(self, amount: kWh):
        discharged_amount = min(amount, self.current_charge)
        self.current_charge -= discharged_amount
        return discharged_amount


class EnergyBalance:
    def __init__(self):
        self.value = kWh(0)

    def add(self, amount: kWh):
        self.value += amount

    def sub(self, amount: kWh):
        self.value -= amount
