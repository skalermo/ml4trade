import unittest

from ml4trade.battery import Battery
from ml4trade.units import MWh


class TestBattery(unittest.TestCase):
    def test_init(self):
        battery = Battery(MWh(0.1), 1.0, MWh(0.05))
        self.assertEqual(battery.current_charge, MWh(0.05))

    def test_charge(self):
        battery = Battery(MWh(0.1), 1.0, MWh(0.05))
        battery.charge(MWh(0.01))
        self.assertAlmostEqual(battery.current_charge.value, 0.06, 10)

    def test_charge_with_overflow(self):
        battery = Battery(MWh(0.1), 1.0, MWh(0.04))
        charged = battery.charge(MWh(0.1))
        self.assertAlmostEqual(charged.value, 0.06, 10)
        self.assertAlmostEqual(battery.current_charge.value, 0.1, 10)

    def test_discharge(self):
        battery = Battery(MWh(0.1), 1.0, MWh(0.05))
        battery.discharge(MWh(0.01))
        self.assertEqual(battery.current_charge, MWh(0.04))

    def test_discharge_with_overflow(self):
        battery = Battery(MWh(0.1), 1.0, MWh(0.04))
        discharged = battery.discharge(MWh(0.1))
        self.assertEqual(discharged, MWh(0.04))
        self.assertEqual(battery.current_charge, MWh(0))

    def test_efficiency_cuts_down_energy_charged(self):
        battery = Battery(MWh(0.1), 0.25, MWh(0.05))
        charged = battery.charge(MWh(0.1))
        # charged amount shows how much energy was used to charge the battery
        # not the amount actually stored into it
        self.assertEqual(charged, MWh(0.1))
        self.assertAlmostEqual(battery.current_charge.value, 0.075, 10)

    def test_efficiency_does_not_affect_discharge(self):
        battery = Battery(MWh(0.1), 0.25, MWh(0.05))
        discharged = battery.discharge(MWh(0.1))

        self.assertEqual(discharged, MWh(0.05))
        self.assertEqual(battery.current_charge, MWh(0))

    def test_efficiency_cant_be_set_to_zero(self):
        with self.assertRaises(AssertionError):
            Battery(MWh(0.1), 0, MWh(0.05))


if __name__ == '__main__':
    unittest.main()
