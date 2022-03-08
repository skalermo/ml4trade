import unittest

from src.battery import Battery
from src.types import Ah


class TestBattery(unittest.TestCase):
    def test_init(self):
        battery = Battery(Ah(100), 1.0, Ah(50))
        self.assertEqual(battery.current_charge, Ah(50))

    def test_charge(self):
        battery = Battery(Ah(100), 1.0, Ah(50))
        battery.charge(Ah(10))
        self.assertEqual(battery.current_charge, Ah(60))

    def test_charge_with_overflow(self):
        battery = Battery(Ah(100), 1.0, Ah(40))
        charged = battery.charge(Ah(100))
        self.assertEqual(charged, Ah(60))
        self.assertEqual(battery.current_charge, Ah(100))

    def test_discharge(self):
        battery = Battery(Ah(100), 1.0, Ah(50))
        battery.discharge(Ah(10))
        self.assertEqual(battery.current_charge, Ah(40))

    def test_discharge_with_overflow(self):
        battery = Battery(Ah(100), 1.0, Ah(40))
        discharged = battery.discharge(Ah(100))
        self.assertEqual(discharged, Ah(40))
        self.assertEqual(battery.current_charge, Ah(0))


if __name__ == '__main__':
    unittest.main()
