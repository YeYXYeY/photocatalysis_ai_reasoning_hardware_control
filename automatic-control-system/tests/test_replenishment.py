import unittest

from workflow.replenishment import get_replenishment_plan


class ReplenishmentPlanTests(unittest.TestCase):
    def test_mobile_station_rack_one_route(self):
        plan = get_replenishment_plan("mobile_station", "reactant_bottle_rack_1")

        self.assertEqual(plan.before_replace, ["mobile_r1_to_liquid"])
        self.assertEqual(plan.after_replace, ["liquid_r1_to_mobile_r1"])

    def test_material_station_rack_four_route(self):
        plan = get_replenishment_plan("material_station", "reactant_bottle_rack_4")

        self.assertEqual(
            plan.before_replace,
            [
                "mobile_r3_to_material_3",
                "material_r4_to_mobile_r4",
                "mobile_r4_to_liquid",
            ],
        )
        self.assertEqual(
            plan.after_replace,
            [
                "liquid_r4_to_mobile_r4",
                "mobile_r4_to_material_4",
                "material_r3_to_mobile_r3",
            ],
        )

    def test_unsupported_route_raises_value_error(self):
        with self.assertRaises(ValueError):
            get_replenishment_plan("material_station", "reactant_bottle_rack_1")


if __name__ == "__main__":
    unittest.main()
