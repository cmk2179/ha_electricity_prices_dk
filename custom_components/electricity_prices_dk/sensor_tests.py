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
from sensor import _find_cheapest_hour_span
from n1_utils import get_tarif_for_hour
from const import LOCAL_TZ


class SensorTests(unittest.TestCase):

    def setUp(self):
        pass

    def test_find_cheapest_hour_span():
        # TODO: Add test..
        pass


if __name__ == "__main__":
    unittest.main()
