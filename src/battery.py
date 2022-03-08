from src.energy_types import KWh


class Battery:
    def __init__(self, capacity: KWh = 100, efficiency: float = 1.0, current_charge: KWh = 0):
        self.capacity = capacity
        self.efficiency = efficiency
        self.current_charge = current_charge

    def charge(self, amount: KWh):
        charged_amount = min(amount, self.capacity - self.current_charge)  # efficiency
        self.current_charge += charged_amount
        return charged_amount

    def discharge(self, amount: KWh):
        discharged_amount = min(amount, self.current_charge)
        self.current_charge -= discharged_amount
        return discharged_amount
