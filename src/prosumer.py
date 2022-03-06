from src.battery import Battery
from src.energy_manipulation.energy_systems import EnergySystems
from src.energy_types import Ah, to_ah, to_kw
from src.market import EnergyMarket
from datetime import date


class Prosumer:
    def __init__(self, battery: Battery, energy_systems: EnergySystems, balance: int = 0, energy_market: EnergyMarket = None, my_date : date = date.today()):
        self.battery = battery
        self.energy_systems = energy_systems
        self.balance = balance
        self.energy_market = energy_market
        self.scheduled_actions = []
        self.my_date = date

    def set_new_actions(self):
        pass

    def consume_energy(self):
        consumption_power = self.energy_systems.get_consumption_power(self.my_date)
        consumed_energy = consumption_power.value * 1000 / 230
        consumed_energy = to_ah(consumed_energy)
        discharged_amount = self.battery.discharge(consumed_energy)
        if discharged_amount < consumed_energy:
            self.buy_energy(consumed_energy - discharged_amount)

    def buy_energy(self, amount: Ah):
        pass

    def consume_and_buy(self):
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
