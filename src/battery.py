from src.energy_types import Ah


class Battery:
    def __init__(self, capacity: Ah, performance: float, current_charge: Ah = 0):
        self.capacity = capacity
        self.performance = performance
        self.current_charge = current_charge

    def charge(self, amount: Ah):
        charged_amount = min(amount, self.capacity - self.current_charge)
        self.current_charge += charged_amount
        return charged_amount

    def discharge(self, amount: Ah):
        discharged_amount = min(amount, self.current_charge)
        self.current_charge -= discharged_amount
        return discharged_amount
