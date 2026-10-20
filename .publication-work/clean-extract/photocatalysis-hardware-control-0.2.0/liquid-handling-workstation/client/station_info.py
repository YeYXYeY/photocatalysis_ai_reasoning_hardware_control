"""Station addresses and command allow-lists used by the client layer."""

station_info = {
    "liquid_station": ("192.0.2.10", 61250),
    "solid_station": ("192.0.2.11", 61250),
    "reactor_station": ("192.0.2.12", 51250),
    "mobile_robot": ("192.0.2.13", 61250),
    "test": ("127.0.0.1", 61250),
}

liquid_station_command_list = [
    "open_cap",  # Open bottle caps.
    "prepare_solution",  # Prepare the reaction solution.
    "pre_nmr_test",  # Run pre-reaction NMR sampling.
    "post_nmr_test",  # Run post-reaction NMR sampling.
    "close_cap",  # Close bottle caps.
]

reactor_station_command = ["start_reaction"]  # Start the reactor workflow.

solid_station_command = ["start_weighing"]  # Start the weighing workflow.

mobile_robot_command_list = [
    "move_to_transit_station",  # Move to the transfer station.
    "liquid_station_take_sample",  # Pick up a sample from the liquid station.
    "reactor_station_take_sample",  # Pick up a sample from the reactor station.
    "solid_station_take_sample",  # Pick up a sample from the solid station.
    "liquid_station_place_sample",  # Place a sample at the liquid station.
    "reactor_station_place_sample",  # Place a sample at the reactor station.
    "solid_station_place_sample",  # Place a sample at the solid station.
]

station_command_dict = {
    "liquid_station": liquid_station_command_list,
    "reactor_station": reactor_station_command,
    "solid_station": solid_station_command,
    "mobile_robot": mobile_robot_command_list,
}
