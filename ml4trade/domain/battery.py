from ml4trade.domain.units import MWh


class Battery:
    def __init__(self, capacity: MWh, efficiency: float, init_charge: MWh = MWh(0)):
        assert efficiency > 0, 'Efficiency must be greater than 0'
        assert MWh(0) <= init_charge <= capacity, 'Initial charge cannot be negative or exceed battery capacity'

        self.capacity = capacity
        self.efficiency = efficiency
        self.current_charge = init_charge

    @property
    def rel_current_charge(self):
        return self.current_charge / self.capacity

    def charge(self, amount: MWh):
        if amount * self.efficiency <= self.capacity - self.current_charge:
            self.current_charge += amount * self.efficiency
            return amount
        charged_amount = self.capacity - self.current_charge
        self.current_charge = self.capacity
        return charged_amount / self.efficiency

    def discharge(self, amount: MWh):
        discharged_amount = min(amount, self.current_charge)
        self.current_charge -= discharged_amount
        return discharged_amount


class EnergyBalance:
    def __init__(self):
        self.value = MWh(0)

    def add(self, amount: MWh):
        self.value += amount

    def sub(self, amount: MWh):
        self.value -= amount
