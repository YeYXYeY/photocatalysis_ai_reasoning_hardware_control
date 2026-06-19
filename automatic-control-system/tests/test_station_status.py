import os
import tempfile
import unittest

import yaml

from station_status.station_status import StationStatus


class StationStatusTests(unittest.TestCase):
    def _make_status_file(self) -> str:
        payload = {
            "liquid_station": {
                "running_status": "ready",
                "chemical_remaining": {"A1": 100.0},
                "bottle_rack": {"bottle_rack_1": "rack_a"},
                "tip_rack": "tip_1",
            },
            "rack_info": {
                "reactant_bottle_rack_1": {"A1": [1, 2]},
            },
        }
        temp_dir = tempfile.mkdtemp()
        status_path = os.path.join(temp_dir, "station_status.yaml")
        with open(status_path, "w", encoding="utf-8") as file:
            yaml.safe_dump(payload, file)
        return status_path

    def test_update_generic_info_persists_to_yaml_file(self):
        status_path = self._make_status_file()
        station_status = StationStatus(status_file=status_path)

        station_status.update_generic_info(
            "liquid_station", "chemical_remaining", {"A1": 42.0}
        )

        with open(status_path, "r", encoding="utf-8") as file:
            persisted = yaml.safe_load(file)
        self.assertEqual(
            persisted["liquid_station"]["chemical_remaining"],
            {"A1": 42.0},
        )

    def test_update_bottle_rack_pos_moves_rack_between_stations(self):
        status_path = self._make_status_file()
        station_status = StationStatus(status_file=status_path)
        station_status.station_status["mobile_station"] = {
            "bottle_rack": {"bottle_rack_2": "none"},
            "running_status": "ready",
        }

        station_status.update_bottle_rack_pos(
            "rack_a", ("mobile_station", "bottle_rack_2")
        )

        self.assertEqual(
            station_status.station_status["liquid_station"]["bottle_rack"][
                "bottle_rack_1"
            ],
            "none",
        )
        self.assertEqual(
            station_status.station_status["mobile_station"]["bottle_rack"][
                "bottle_rack_2"
            ],
            "rack_a",
        )


if __name__ == "__main__":
    unittest.main()
