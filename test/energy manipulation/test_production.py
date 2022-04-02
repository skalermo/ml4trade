import datetime
import unittest

from src.custom_types import kW
from src.energy_manipulation.production import ProductionSystem, WindSystem


class TestProduction(unittest.TestCase):
    def test_wind_production(self):
        wind_production_system = WindSystem()
        _datetime = datetime.datetime(2022, 2, 2, 10)
        power = wind_production_system.get_power(_datetime)
        calculated_power = 8*10/11
        self.assertEqual(power.value, calculated_power)


if __name__ == '__main__':
    unittest.main()
