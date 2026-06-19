from dataclasses import dataclass


@dataclass(frozen=True)
class ReplenishmentPlan:
    before_replace: list[str]
    after_replace: list[str]


_REPLENISHMENT_ROUTES: dict[tuple[str, str], ReplenishmentPlan] = {
    (
        "material_station",
        "reactant_bottle_rack_4",
    ): ReplenishmentPlan(
        before_replace=[
            "mobile_r3_to_material_3",
            "material_r4_to_mobile_r4",
            "mobile_r4_to_liquid",
        ],
        after_replace=[
            "liquid_r4_to_mobile_r4",
            "mobile_r4_to_material_4",
            "material_r3_to_mobile_r3",
        ],
    ),
    (
        "mobile_station",
        "reactant_bottle_rack_1",
    ): ReplenishmentPlan(
        before_replace=["mobile_r1_to_liquid"],
        after_replace=["liquid_r1_to_mobile_r1"],
    ),
    (
        "mobile_station",
        "reactant_bottle_rack_2",
    ): ReplenishmentPlan(
        before_replace=["mobile_r2_to_liquid"],
        after_replace=["liquid_r2_to_mobile_r2"],
    ),
    (
        "mobile_station",
        "reactant_bottle_rack_3",
    ): ReplenishmentPlan(
        before_replace=["mobile_r3_to_liquid"],
        after_replace=["liquid_r3_to_mobile_r3"],
    ),
}


def get_replenishment_plan(station_name: str, rack_name: str) -> ReplenishmentPlan:
    """Return the robot-movement plan required to replace reagents for a rack."""
    try:
        return _REPLENISHMENT_ROUTES[(station_name, rack_name)]
    except KeyError as error:
        raise ValueError(
            f"No replenishment route is defined for station '{station_name}' and rack '{rack_name}'."
        ) from error
