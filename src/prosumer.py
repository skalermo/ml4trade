from src.battery import Battery
from src.energy_manipulation.energy_systems import EnergySystems
from src.market import EnergyMarket


class Prosumer:
    def __init__(self, battery: Battery, energy_systems: EnergySystems, balance: int = 0, energy_market: EnergyMarket = None):
        self.battery = battery
        self.energy_systems = energy_systems
        self.balance = balance
        self.energy_market = energy_market
        self.scheduled_actions = []

    def set_new_actions(self):
        pass

    def consume_energy(self):
        pass

    def produce_energy(self):
        pass

    def sell_energy(self):
        pass

    def produce_and_sell(self):
        pass

    def send_transaction(self):
        pass

    def schedule(self, action):
        pass

    def get_scheduled_buy_amount(self, hour: int):
        pass

    def get_scheduled_sell_amount(self, hour: int):
        pass
