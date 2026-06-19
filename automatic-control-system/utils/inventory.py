from station_status.station_status import StationStatus


def find_station_by_rack_name(status, rack_name):
    """Return the station currently holding the named bottle rack."""
    for station_name, details in status.items():
        bottle_racks = details.get("bottle_rack", {})
        for bottle_name in bottle_racks.values():
            if bottle_name == rack_name:
                return station_name
    return "None"


def check_remaining(station_id, consumption_dict):
    """
    Check whether a station has enough remaining reagent volume.

    Returns:
        Liquid station: `(result, chemical_list, rack_list, replacing_dict)`
        Solid station: `chemical_list`
    """
    station_status = StationStatus()
    if station_id == "liquid_station":
        remaining_dict = station_status.station_status[station_id]["chemical_remaining"]
        if set(remaining_dict.keys()) == set(consumption_dict.keys()) or set(
            remaining_dict.keys()
        ) - set(consumption_dict.keys()) == {"G5", "G6"}:
            result = {
                key: remaining_dict[key] >= consumption_dict[key]
                for key in consumption_dict
            }
            chemical_list = [key for key, value in result.items() if not value]

            replacing_dict = {}
            for rack_name, rack_contents in station_status.station_status[
                "rack_info"
            ].items():
                for chemical in chemical_list:
                    if chemical not in rack_contents:
                        continue
                    if not rack_contents[chemical]:
                        raise ValueError(
                            f"Cannot find {chemical} in {rack_name}; please replenish the rack."
                        )
                    replacing_dict.setdefault(rack_name, {})[chemical] = rack_contents[
                        chemical
                    ][0]
                    rack_contents[chemical].pop(0)

            rack_list = list(replacing_dict.keys())
            station_status.save_status()
            return result, chemical_list, rack_list, replacing_dict

        return "Error: dictionary keys do not match exactly."

    if station_id == "solid_station":
        remaining_dict = station_status.station_status[station_id]["chemical_remaining"]
        if set(remaining_dict.keys()) == set(consumption_dict.keys()):
            result = {
                key: remaining_dict[key] >= consumption_dict[key]
                for key in remaining_dict
            }
            return [key for key, value in result.items() if not value]
        return []

    raise ValueError(f"Unsupported station id: {station_id}")


def replenish_chemicals(replacing_dict):
    """
    Reset replenished liquid-station reagents to their full amount.

    Args:
        replacing_dict: Mapping of chemicals that were replenished.
    """
    station_status = StationStatus()
    for chemical in replacing_dict.keys():
        station_status.station_status["liquid_station"]["chemical_remaining"].update(
            {chemical: 8000}
        )
    station_status.save_status()


def update_remaining(station_id, consumption_dict):
    """
    Subtract consumption from the current station inventory.

    Returns:
        Updated remaining volume dictionary or an error string.
    """
    station_status = StationStatus()
    remaining_dict = station_status.station_status[station_id]["chemical_remaining"]
    if set(remaining_dict.keys()) == set(consumption_dict.keys()) and set(
        remaining_dict.keys()
    ) == set(station_status.station_status[station_id]["chemical_remaining"].keys()):
        for key in remaining_dict:
            if remaining_dict[key] < consumption_dict[key]:
                return "Error: insufficient chemical inventory, please check."
        result = {
            key: remaining_dict[key] - consumption_dict[key] for key in remaining_dict
        }
        station_status.update_generic_info(station_id, "chemical_remaining", result)
        return result

    return "Error: dictionary keys do not match exactly."


def replacing_rack_list(replacing_dict):
    """Return the rack names that need reagent replacement."""
    return list(replacing_dict.keys())
