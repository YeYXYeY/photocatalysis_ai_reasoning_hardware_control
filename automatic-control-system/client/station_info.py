# Station connection information used by the control client.
station_info = {
    "liquid_station": ("192.0.2.10", 61250),
    "solid_station": ("192.0.2.11", 61250),
    "reactor_station": ("192.0.2.12", 51250),
    "mobile_robot": ("192.0.2.13", 61250),
    "peptide_station": ("192.0.2.14", 61250),
    "test": ("127.0.0.1", 61250),
}

station_status = {
    "liquid_station": "idle",
    "solid_station": "idle",
    "reactor_station": "idle",
    "mobile_robot": "idle",
}

# Supported commands for the liquid station.
liquid_station_command_list = [
    "open_cap",  # Open the cap.
    "prepare_solution",  # Prepare the solution.
    "pre_nmr_test",  # Run the pre-reaction NMR workflow.
    "post_nmr_test",  # Run the post-reaction NMR workflow.
    "close_cap",  # Close the cap.
    "tip_rack_out",  # Move the tip rack out.
    "tip_rack_back",  # Move the tip rack back.
    "replace_reactants",  # Replace depleted reactants.
]

# Supported commands for the reactor station.
reactor_station_command = ["start_reactor", "stop_reactor"]

# Supported commands for the solid station.
solid_station_command = ["weighing", "push_rack_out", "pull_rack_back"]

# Supported transfer commands for the mobile robot.
mobile_robot_command_list = [
    # Mobile station to other stations.
    "mobile_1_to_liquid",  # Move reaction bottle rack 1 to the liquid station.
    "mobile_2_to_liquid",  # Move reaction bottle rack 2 to the liquid station.
    "mobile_r1_to_liquid",  # Move reactant rack r1 to the liquid station.
    "mobile_r2_to_liquid",  # Move reactant rack r2 to the liquid station.
    "mobile_r3_to_liquid",  # Move reactant rack r3 to the liquid station.
    "mobile_r4_to_liquid",  # Move reactant rack r4 to the liquid station.
    "mobile_t1_to_liquid",  # Move tip rack 1 to the liquid station.
    "mobile_2_to_solid",  # Move reaction bottle rack 2 to the solid station.
    "mobile_2_to_reactor",  # Move reaction bottle rack 2 to the reactor station.
    "mobile_t2_to_material_t1",  # Move tip rack 2 to slot t1 on the material station.
    "mobile_t2_to_material_t2",  # Move tip rack 2 to slot t2 on the material station.
    "mobile_r3_to_material_r3",  # Move reactant rack r3 to slot r3 on the material station.
    "mobile_r4_to_material_r4",  # Move reactant rack r4 to slot r4 on the material station.
    "mobile_1_to_material_1",  # Move reaction bottle rack 1 to slot 1 on the material station.
    "mobile_2_to_material_2",  # Move reaction bottle rack 2 to slot 2 on the material station.
    # Liquid station to mobile station.
    "liquid_1_to_mobile_1",  # Move reaction bottle rack 1 to the mobile station.
    "liquid_2_to_mobile_2",  # Move reaction bottle rack 2 to the mobile station.
    "liquid_r1_to_mobile_r1",  # Move reactant rack r1 to the mobile station.
    "liquid_r2_to_mobile_r2",  # Move reactant rack r2 to the mobile station.
    "liquid_r3_to_mobile_r3",  # Move reactant rack r3 to the mobile station.
    "liquid_r4_to_mobile_r4",  # Move reactant rack r4 to the mobile station.
    "liquid_t1_to_mobile_t2",  # Move tip rack 1 to slot t2 on the mobile station.
    # Solid station to mobile station.
    "solid_2_to_mobile_2",  # Move reaction bottle rack 2 to the mobile station.
    # Reactor station to mobile station.
    "reactor_2_to_mobile_2",  # Move reaction bottle rack 2 to the mobile station.
    # Material station to mobile station.
    "material_t1_to_mobile_t1",  # Move tip rack 1 to the mobile station.
    "material_t2_to_mobile_t1",  # Move tip rack 2 to the mobile station.
    "material_r3_to_mobile_r3",  # Move reactant rack r3 to slot r3 on the mobile station.
    "material_r4_to_mobile_r4",  # Move reactant rack r4 to slot r4 on the mobile station.
    "material_1_to_mobile_1",  # Move reaction bottle rack 1 to the mobile station.
    "material_2_to_mobile_2",  # Move reaction bottle rack 2 to the mobile station.
]

peptide_station_command_list = ["start_peptide", "push_rack_out", "pull_rack_back"]

# Station command lookup table used by the client command dispatcher.
station_command_dict = {
    "liquid_station": liquid_station_command_list,
    "reactor_station": reactor_station_command,
    "solid_station": solid_station_command,
    "mobile_robot": mobile_robot_command_list,
    "peptide_station": peptide_station_command_list,
}
