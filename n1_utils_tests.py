import unittest
from itertools import chain
from datetime import datetime
from n1_utils import get_tarif_for_hour


class N1UtilsTests(unittest.TestCase):

    def setUp(self):
        self.tarifs = {
            "low_load_summer": 0.0867,
            "high_load_summer": 0.13,
            "peak_load_summer": 0.33799999999999997,
            "low_load_winter": 0.0867,
            "high_load_winter": 0.26,
            "peak_load_winter": 0.7801,
        }

        current_year = datetime.now().year
        self.base_date = datetime(current_year, 1, 1)

    def act(self, months, hours, expected):
        for month in months:
            for hour in hours:
                date = datetime(self.base_date.year, month, 1, hour)
                self.assertEqual(
                    get_tarif_for_hour(date, self.tarifs),
                    expected,
                    f"Expected {expected} for {date.strftime("%Y-%m-%dT%H:%M")}",
                )

    def test_get_tarifs_low_load_summer(self):
        self.act(
            range(4, 10),
            range(0, 6),
            self.tarifs["low_load_summer"],
        )

    def test_get_tarifs_high_load_summer(self):
        self.act(range(4, 10), range(6, 17), self.tarifs["high_load_summer"])

    def test_get_tarifs_peak_load_summer(self):
        self.act(range(4, 10), range(17, 21), self.tarifs["peak_load_summer"])

    def test_get_tarifs_low_load_winter(self):
        self.act(
            chain(range(10, 13), range(1, 3)),
            range(0, 6),
            self.tarifs["low_load_winter"],
        )

    def test_get_tarifs_high_load_winter(self):
        self.act(
            chain(range(10, 13), range(1, 3)),
            range(6, 17),
            self.tarifs["high_load_winter"],
        )

    def test_get_tarifs_peak_load_winter(self):
        self.act(
            chain(range(10, 13), range(1, 3)),
            range(17, 21),
            self.tarifs["peak_load_winter"],
        )


if __name__ == "__main__":
    unittest.main()
