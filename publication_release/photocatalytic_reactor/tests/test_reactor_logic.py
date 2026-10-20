import unittest

from app.reactor_logic import (
    clamp_cooling_output,
    clamp_shaker_speed,
    encode_shaker_speed,
    normalize_cooling_mode,
    should_enter_reaction_phase,
)


class ReactorLogicTests(unittest.TestCase):
    def test_normalize_cooling_mode_accepts_supported_values(self) -> None:
        self.assertEqual(normalize_cooling_mode(0), 0)
        self.assertEqual(normalize_cooling_mode(1), 1)
        self.assertEqual(normalize_cooling_mode(2), 2)

    def test_normalize_cooling_mode_rejects_unsupported_values(self) -> None:
        with self.assertRaises(ValueError):
            normalize_cooling_mode(3)

    def test_clamp_shaker_speed_limits_values_to_supported_range(self) -> None:
        self.assertEqual(clamp_shaker_speed(-5), 0)
        self.assertEqual(clamp_shaker_speed(80), 80)
        self.assertEqual(clamp_shaker_speed(999), 120)

    def test_encode_shaker_speed_returns_two_byte_hex_string(self) -> None:
        self.assertEqual(encode_shaker_speed(0), "00 00")
        self.assertEqual(encode_shaker_speed(100), "00 64")
        self.assertEqual(encode_shaker_speed(120), "00 78")

    def test_clamp_cooling_output_applies_base_offset_and_bounds(self) -> None:
        self.assertEqual(clamp_cooling_output(-80.0, 25.0), 0.0)
        self.assertEqual(clamp_cooling_output(10.0, 25.0), 35.0)
        self.assertEqual(clamp_cooling_output(90.0, 25.0), 100.0)

    def test_should_enter_reaction_phase_uses_tolerance_window(self) -> None:
        self.assertTrue(should_enter_reaction_phase(20.4, 20.0, tolerance=0.5))
        self.assertFalse(should_enter_reaction_phase(20.6, 20.0, tolerance=0.5))


if __name__ == "__main__":
    unittest.main()
