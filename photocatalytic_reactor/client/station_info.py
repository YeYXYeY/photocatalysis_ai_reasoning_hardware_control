"""Station connection metadata and allowed remote commands."""

station_info = {
    "liquid_station": ("192.0.2.10", 61250),
    "solid_station": ("192.0.2.11", 61250),
    "reactor_station": ("192.0.2.12", 51250),
    "mobile_robot": ("192.0.2.13", 61250),
    "peptide_station": ("192.0.2.14", 61250),
    "test": ("127.0.0.1", 61250),
}

liquid_station_command_list = [
    "open_cap",
    "prepare_solution",
    "pre_nmr_test",
    "post_nmr_test",
    "close_cap",
]

reactor_station_command_list = [
    "start_reactor",
    "start_reaction",
    "stop_reactor",
]
solid_station_command_list = ["start_weighing"]

mobile_robot_command_list = [
    "move_to_transit_station",
    "liquid_station_take_sample",
    "reactor_station_take_sample",
    "solid_station_take_sample",
    "liquid_station_place_sample",
    "reactor_station_place_sample",
    "solid_station_place_sample",
]

peptide_station_command_list = [
    "start_synthesis",
    "add_reagent",
]

station_command_dict = {
    "liquid_station": liquid_station_command_list,
    "reactor_station": reactor_station_command_list,
    "solid_station": solid_station_command_list,
    "mobile_robot": mobile_robot_command_list,
    "peptide_station": peptide_station_command_list,
}
