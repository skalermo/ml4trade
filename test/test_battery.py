import unittest

from src.battery import Battery
from src.custom_types import kWh


class TestBattery(unittest.TestCase):
    def test_init(self):
        battery = Battery(kWh(100), 1.0, kWh(50))
        self.assertEqual(battery.current_charge, kWh(50))

    def test_charge(self):
        battery = Battery(kWh(100), 1.0, kWh(50))
        battery.charge(kWh(10))
        self.assertEqual(battery.current_charge, kWh(60))

    def test_charge_with_overflow(self):
        battery = Battery(kWh(100), 1.0, kWh(40))
        charged = battery.charge(kWh(100))
        self.assertEqual(charged, kWh(60))
        self.assertEqual(battery.current_charge, kWh(100))

    def test_discharge(self):
        battery = Battery(kWh(100), 1.0, kWh(50))
        battery.discharge(kWh(10))
        self.assertEqual(battery.current_charge, kWh(40))

    def test_discharge_with_overflow(self):
        battery = Battery(kWh(100), 1.0, kWh(40))
        discharged = battery.discharge(kWh(100))
        self.assertEqual(discharged, kWh(40))
        self.assertEqual(battery.current_charge, kWh(0))

    def test_efficiency_cuts_down_energy_charged(self):
        battery = Battery(kWh(100), 0.25, kWh(50))
        charged = battery.charge(kWh(100))
        # not sure whether we want to return amount of
        # energy used or energy stored in battery
        self.assertEqual(charged, kWh(100))
        self.assertEqual(battery.current_charge, kWh(75))

    def test_efficiency_does_not_affect_discharge(self):
        battery = Battery(kWh(100), 0.25, kWh(50))
        discharged = battery.discharge(kWh(100))

        self.assertEqual(discharged, kWh(50))
        self.assertEqual(battery.current_charge, kWh(0))


if __name__ == '__main__':
    unittest.main()
