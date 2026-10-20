from utils.inventory import (
    check_remaining,
    find_station_by_rack_name,
    replenish_chemicals,
    replacing_rack_list,
    update_remaining,
)
from utils.task_processing import (
    calculate_liquid_consumption,
    calculate_solid_consumption,
    split_task,
)


def calc_liquid_comsumption(liquid_task_df, flag=0):
    """Compatibility wrapper for the historic liquid-consumption helper name."""
    return calculate_liquid_consumption(liquid_task_df, mode=flag)


def calc_solid_comsumption(solid_task_df):
    """Compatibility wrapper for the historic solid-consumption helper name."""
    return calculate_solid_consumption(solid_task_df)


def find_station_by_rackname(status, name):
    """Compatibility wrapper for the historic rack lookup helper name."""
    return find_station_by_rack_name(status, name)


def sup_chemicals(replacing_dict):
    """Compatibility wrapper for the historic replenishment helper name."""
    return replenish_chemicals(replacing_dict)
