from typing import Any


def build_station_info_sections(station_status: dict[str, Any]) -> dict[str, list[str]]:
    """Convert station status data into display-ready text blocks."""
    sections: dict[str, list[str]] = {}

    if "liquid_station" in station_status:
        liquid = station_status["liquid_station"]
        sections["liquid_station"] = [
            f'Reaction Bottle Rack: {liquid["bottle_rack"]["bottle_rack_1"]}',
            f'Running Status: {liquid["running_status"]}',
            f'Tip Rack: {liquid["tip_rack"]}',
            f'Chemical Remaining: {liquid["chemical_remaining"]}',
        ]

    if "solid_station" in station_status:
        solid = station_status["solid_station"]
        sections["solid_station"] = [
            f'Reaction Bottle Rack: {solid["bottle_rack"]["bottle_rack_1"]}',
            f'Running Status: {solid["running_status"]}',
            f'Chemical Remaining: {solid["chemical_remaining"]}',
        ]

    if "reactor_station" in station_status:
        reactor = station_status["reactor_station"]
        sections["reactor_station"] = [
            f'Reaction Bottle Rack: {reactor["bottle_rack"]["bottle_rack_1"]}',
            f'Running Status: {reactor["running_status"]}',
        ]

    if "rack_info" in station_status:
        rack_info = station_status["rack_info"]
        sections["rack_info"] = [
            f'Reactant Bottle Rack 1: {rack_info["reactant_bottle_rack_1"]}',
            f'Reactant Bottle Rack 2: {rack_info["reactant_bottle_rack_2"]}',
            f'Reactant Bottle Rack 3: {rack_info["reactant_bottle_rack_3"]}',
            f'Reactant Bottle Rack 4: {rack_info["reactant_bottle_rack_4"]}',
        ]

    if "mobile_station" in station_status:
        mobile = station_status["mobile_station"]
        sections["mobile_station"] = [
            f'Running Status: {mobile["running_status"]}',
            f'Tip Rack Info: {mobile["tip_rack"]}',
            f'Bottle Rack Info: {mobile["bottle_rack"]}',
        ]

    if "peptide_station" in station_status:
        peptide = station_status["peptide_station"]
        sections["peptide_station"] = [
            f'Reaction Bottle Rack: {peptide["bottle_rack"]["bottle_rack_1"]}',
            f'Running Status: {peptide["running_status"]}',
        ]

    return sections
