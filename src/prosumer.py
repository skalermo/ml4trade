from src.battery import Battery
from src.energy_manipulation.energy_systems import EnergySystems
from src.energy_types import KWh
from src.market import EnergyMarket
from datetime import date


class Prosumer:
    def __init__(self, battery: Battery, energy_systems: EnergySystems, balance: int = 0,
                 energy_market: EnergyMarket = None, my_date: date = date.today()):
        self.my_date = my_date
        self.battery = battery
        self.energy_systems = energy_systems
        self.balance = balance
        self.energy_market = energy_market
        self.scheduled_actions = []

    def set_new_actions(self):
        pass

    def consume_energy(self, hour: int):
        consumption_power = self.energy_systems.get_consumption_power(self.my_date)
        consumed_amount = KWh(consumption_power.value)
        bought_amount = self.get_scheduled_buy_amount(hour)
        consumed_amount -= bought_amount
        if consumed_amount.value > 0:
            discharged_amount = self.battery.discharge(consumed_amount)
            if discharged_amount < consumed_amount:
                needed_energy = consumed_amount - discharged_amount
                self.buy_energy(needed_energy, 1.2*self.get_scheduled_price(hour))
        elif consumed_amount.value < 0:
            consumed_amount *= -1
            charged_amount = self.battery.charge(consumed_amount)
            deficient_amount = consumed_amount - charged_amount
            if deficient_amount.value > 0:
                self.sell_energy(deficient_amount, 0.8*self.get_scheduled_price(hour))

    def buy_energy(self, amount: KWh, price: float) -> float:
        return self.energy_market.buy(amount, price)

    def produce_energy(self):
        pass

    def sell_energy(self, amount: KWh, price: float):
        return self.energy_market.sell(amount, price)

    def produce_and_sell(self):
        pass

    def send_transaction(self):
        pass

    def schedule(self, action):
        pass

    def get_scheduled_buy_amount(self, hour: int) -> KWh:
        pass

    def get_scheduled_sell_amount(self, hour: int) -> KWh:
        pass

    def get_scheduled_price(self, hour: int) -> float:
        pass
