# An integration for Home Assistant that fetches electricity prices and makes the data available via sensors.
# Copyright (C) 2025  Chris Opstrup

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import unittest
from itertools import chain
from datetime import datetime
from n1_utils import get_tarif_for_hour
from consts import LOCAL_TZ


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

        self.summer_months = range(4, 10)
        self.winter_months = chain(range(10, 13), range(1, 3))

        self.low_load_hours = range(0, 6)
        self.high_load_hours = chain(range(6, 17), range(21, 23))
        self.peak_load_hours = range(17, 21)

        current_year = datetime.now(LOCAL_TZ).year
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
            self.summer_months,
            self.low_load_hours,
            self.tarifs["low_load_summer"],
        )

    def test_get_tarifs_high_load_summer(self):
        self.act(
            self.summer_months, self.high_load_hours, self.tarifs["high_load_summer"]
        )

    def test_get_tarifs_peak_load_summer(self):
        self.act(
            self.summer_months, self.peak_load_hours, self.tarifs["peak_load_summer"]
        )

    def test_get_tarifs_low_load_winter(self):
        self.act(
            self.winter_months,
            self.low_load_hours,
            self.tarifs["low_load_winter"],
        )

    def test_get_tarifs_high_load_winter(self):
        self.act(
            self.winter_months,
            self.high_load_hours,
            self.tarifs["high_load_winter"],
        )

    def test_get_tarifs_peak_load_winter(self):
        self.act(
            self.winter_months,
            self.peak_load_hours,
            self.tarifs["peak_load_winter"],
        )


if __name__ == "__main__":
    unittest.main()
