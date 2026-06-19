import os
from typing import NamedTuple

import yaml


class Position(NamedTuple):
    station_id: str
    rack_id: str


class StationStatus:
    def __init__(self, status_file: str | None = None):
        status_folder_path = os.path.dirname(os.path.abspath(__file__))
        self.status_folder_path = status_folder_path
        self.status_file = status_file or os.path.join(
            self.status_folder_path, "station_status.yaml"
        )
        self.station_status = self.load_status()

    def load_status(self):
        """Load station status information from the YAML file."""
        try:
            with open(self.status_file, "r", encoding="utf-8") as file:
                return yaml.safe_load(file) or {}
        except FileNotFoundError:
            print("Status file not found. A new status file will be created.")
            return {}

    def save_status(self):
        """Persist station status information to the YAML file."""
        with open(self.status_file, "w", encoding="utf-8") as file:
            yaml.safe_dump(self.station_status, file, sort_keys=False)

    def update_status(self, station_id, status_info, update_only=False):
        """
        Update the status entry for a station.

        Args:
            station_id: Station identifier.
            status_info: Dictionary with station status fields.
            update_only: When True, update only the provided fields.
        """
        if update_only and station_id in self.station_status:
            self.station_status[station_id].update(status_info)
        else:
            self.station_status[station_id] = status_info
        self.save_status()
        print(f"Updated status for station {station_id}.")

    def query_status(self, station_id):
        """
        Query the status entry for a station.

        Args:
            station_id: Station identifier.
        """
        return self.station_status.get(station_id, "Station not found.")

    def liquid_status(self):
        """Query the status of `liquid_station`."""
        return self.query_status("liquid_station")

    def solid_status(self):
        """Query the status of `solid_station`."""
        return self.query_status("solid_station")

    def mobile_status(self):
        """Query the status of `mobile_station`."""
        return self.query_status("mobile_station")

    def reactor_status(self):
        """Query the status of `reactor_station`."""
        return self.query_status("reactor_station")

    def material_status(self):
        """Query the status of `material_station`."""
        return self.query_status("material_station")

    def rack_info(self):
        """Query the rack information entry."""
        return self.query_status("rack_info")

    def update_generic_info(self, station_id: str, info_key: str, info_value):
        """Update a single named field under a station entry."""
        if station_id in self.station_status:
            if info_key in self.station_status[station_id]:
                self.station_status[station_id][info_key] = info_value
                self.save_status()
                print(f"Updated {info_key} for station {station_id}.")
            else:
                print(f"Station {station_id} is missing '{info_key}', cannot update.")
        else:
            print(f"Station {station_id} was not found.")

    def update_chemical_remaining(self, chemical_name, new_amount):
        """
        Update the remaining amount for a chemical.

        Args:
            chemical_name: Chemical name.
            new_amount: New remaining amount.
        """
        updated = False
        for _, station_info in self.station_status.items():
            if (
                "chemical_remaining" in station_info
                and chemical_name in station_info["chemical_remaining"]
            ):
                station_info["chemical_remaining"][chemical_name] = new_amount
                updated = True
        if updated:
            self.save_status()
            print(f"Updated remaining amount of {chemical_name} to {new_amount}.")
        else:
            print(f"Chemical {chemical_name} was not found.")

    def update_material_rack_info(self, rack_name: str, status: str):
        """
        Update the status of a material rack.

        Args:
            rack_name: Rack name.
            status: New rack status.
        """
        valid_rack_names = [
            "reaction_rack_1",
            "reaction_rack_2",
            "tip_rack_1",
            "tip_rack_2",
        ]
        if rack_name not in valid_rack_names:
            print(f"Invalid rack name: {rack_name}")
            return
        rack_info = self.station_status.get("rack_info", {})
        rack_info[rack_name] = status
        self.station_status["rack_info"] = rack_info
        self.save_status()
        print(f"Updated rack {rack_name} status to {status}.")

    def update_reactant_info(
        self, rack_name: str, chemical_name: str, positions: list[int]
    ):
        """
        Update chemical position information inside a reactant rack.

        Args:
            rack_name: Rack name.
            chemical_name: Chemical name.
            positions: List of slot numbers for the chemical.
        """
        rack_info = self.station_status.get("rack_info", {})

        if rack_name not in rack_info:
            print(f"Rack {rack_name} does not exist and cannot be updated.")
            return

        if chemical_name not in rack_info[rack_name]:
            print(f"Chemical {chemical_name} does not exist in rack {rack_name}.")
            return

        rack_info[rack_name][chemical_name] = positions
        self.station_status["rack_info"] = rack_info
        self.save_status()
        print(f"Updated positions of {chemical_name} in rack {rack_name}.")

    def update_station_status(self, station_id: str, new_status: str):
        """Update the running status of a station."""
        if station_id in self.station_status:
            if "running_status" in self.station_status[station_id]:
                self.station_status[station_id]["running_status"] = new_status
                self.save_status()
                print(f"Updated running status of {station_id} to {new_status}.")
            else:
                print(f"Station {station_id} is missing 'running_status'.")
        else:
            print(f"Station {station_id} was not found.")

    def update_bottle_rack(self, station_id: str, bottle_rack_info: str | dict):
        """Update bottle rack information for a station."""
        if station_id in self.station_status:
            if "bottle_rack" in self.station_status[station_id]:
                self.station_status[station_id]["bottle_rack"] = bottle_rack_info
                self.save_status()
                print(f"Updated bottle rack information for station {station_id}.")
            else:
                print(f"Station {station_id} is missing 'bottle_rack'.")
        else:
            print(f"Station {station_id} was not found.")

    def update_tip_rack(self, station_id: str, tip_rack_info: str | dict):
        """Update tip rack information for a station."""
        if station_id in self.station_status:
            if "tip_rack" in self.station_status[station_id]:
                self.station_status[station_id]["tip_rack"] = tip_rack_info
                self.save_status()
                print(f"Updated tip rack information for station {station_id}.")
            else:
                print(f"Station {station_id} is missing 'tip_rack'.")
        else:
            print(f"Station {station_id} was not found.")

    def update_bottle_rack_pos(self, bottle_rack_name: str, pos: tuple[str, str]):
        """
        Update the location of a bottle rack.

        Args:
            bottle_rack_name: Bottle rack name.
            pos: New location in the form `(station_id, rack_id)`.
        """
        station, rack_id = pos
        for station_name, station_info in self.station_status.items():
            if "bottle_rack" in station_info:
                for rack_name, rack_value in station_info["bottle_rack"].items():
                    print(f"rack_name: {rack_name}, rack_value: {rack_value}")
                    if rack_value == bottle_rack_name:
                        self.station_status[station_name]["bottle_rack"][
                            rack_name
                        ] = "none"
                    if station_name == station and rack_name == rack_id:
                        self.station_status[station_name]["bottle_rack"][
                            rack_id
                        ] = bottle_rack_name
        self.save_status()
        print(f"Updated bottle rack {bottle_rack_name} position to {pos}.")


def extract_chemicals_info(df):
    """
    Extract chemical replacement information from a DataFrame.

    Args:
        df: DataFrame with `NO`, `Chemicals`, and `Replaceable` columns.

    Returns:
        Mapping from chemical name to the list of `NO` values whose rows are replaceable.
    """
    chemicals_dict = {}

    for _, row in df.iterrows():
        chemical = row["Chemicals"]
        replaceable = row["Replaceable"]
        no = row["NO"]

        if replaceable == 1:
            if chemical in chemicals_dict:
                chemicals_dict[chemical].append(no)
            else:
                chemicals_dict[chemical] = [no]

    return chemicals_dict


if __name__ == "__main__":
    station_status = StationStatus()
    print(station_status.load_status())
