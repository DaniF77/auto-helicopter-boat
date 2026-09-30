"""Тесты для автовертолодки.

Модульные тесты написаны по паттерну AAA (Arrange / Act / Assert).
Сценарные тесты написаны по GWT (Given / When / Then) через пилота.
В имени каждого теста есть ID из TEST_CASES.md.

Запуск из корня проекта:  python -m unittest discover -s tests -v
"""
import unittest

from auto_helicopter_boat import (
    AutoHelicopterBoat,
    BoatOutOfEnergy,
    BoatSinks,
    BoatWrongMode,
)


def make(**changes):
    """Создаёт автовертолодку со стандартными параметрами из TEST_CASES.md."""
    params = {
        "name": "Автовертолодка",
        "mass_kg": 500.0,
        "hull_volume_m3": 1.0,
        "max_speed_kmh": 100.0,
    }
    params.update(changes)
    return AutoHelicopterBoat(**params)


class Pilot:
    """Пилот: короткие команды для сценарных тестов."""

    def __init__(self, vehicle):
        self.vehicle = vehicle
        self.last_hours = None

    def sail(self, km):
        self.last_hours = self.vehicle.move(km, "water")

    def drive(self, km):
        self.last_hours = self.vehicle.move(km, "ground")

    def fly(self, km):
        self.last_hours = self.vehicle.move(km, "air")

    def switch(self, mode):
        self.vehicle.switch_mode(mode)


# ---------------------------------------------------------------------------
# Модульные тесты
# ---------------------------------------------------------------------------

class TestConstructor(unittest.TestCase):
    def test_TC_01_empty_name_raises_value_error(self):
        with self.assertRaises(ValueError):
            make(name="")

    def test_TC_02_zero_mass_raises_value_error(self):
        with self.assertRaises(ValueError):
            make(mass_kg=0)

    def test_TC_03_negative_hull_volume_raises_value_error(self):
        with self.assertRaises(ValueError):
            make(hull_volume_m3=-1)

    def test_TC_04_zero_max_speed_raises_value_error(self):
        with self.assertRaises(ValueError):
            make(max_speed_kmh=0)

    def test_TC_05_energy_above_100_raises_value_error(self):
        with self.assertRaises(ValueError):
            make(energy=101)

    def test_TC_06_negative_energy_raises_value_error(self):
        with self.assertRaises(ValueError):
            make(energy=-1)

    def test_TC_07_default_state(self):
        # Arrange + Act
        boat = make()
        # Assert
        self.assertEqual(boat.energy, 100)
        self.assertEqual(boat.mode, "water")
        self.assertEqual(boat.position_km, 0)
        self.assertFalse(boat.is_flying)


class TestSwitchMode(unittest.TestCase):
    def test_TC_08_switch_to_ground(self):
        boat = make()
        boat.switch_mode("ground")
        self.assertEqual(boat.mode, "ground")
        self.assertEqual(boat.energy, 95)
        self.assertFalse(boat.is_flying)

    def test_TC_09_switch_to_air(self):
        boat = make()
        boat.switch_mode("air")
        self.assertEqual(boat.mode, "air")
        self.assertEqual(boat.energy, 90)
        self.assertTrue(boat.is_flying)

    def test_TC_10_unknown_mode_raises_value_error(self):
        boat = make()
        with self.assertRaises(ValueError):
            boat.switch_mode("space")

    def test_TC_11_same_mode_changes_nothing(self):
        boat = make()
        boat.switch_mode("water")
        self.assertEqual(boat.mode, "water")
        self.assertEqual(boat.energy, 100)

    def test_TC_12_not_enough_energy_raises_and_keeps_state(self):
        boat = make(energy=4)
        with self.assertRaises(BoatOutOfEnergy):
            boat.switch_mode("ground")
        self.assertEqual(boat.mode, "water")
        self.assertEqual(boat.energy, 4)


class TestMove(unittest.TestCase):
    def test_TC_13_move_on_water(self):
        boat = make()
        hours = boat.move(10, "water")
        self.assertAlmostEqual(hours, 0.2)
        self.assertEqual(boat.energy, 90)
        self.assertEqual(boat.position_km, 10)

    def test_TC_14_move_on_ground(self):
        boat = make()
        boat.switch_mode("ground")  # energy = 95
        hours = boat.move(40, "ground")
        self.assertAlmostEqual(hours, 0.5)
        self.assertEqual(boat.energy, 35)
        self.assertEqual(boat.position_km, 40)

    def test_TC_15_move_in_air(self):
        boat = make()
        boat.switch_mode("air")  # energy = 90
        hours = boat.move(10, "air")
        self.assertAlmostEqual(hours, 0.1)
        self.assertEqual(boat.energy, 60)
        self.assertEqual(boat.position_km, 10)
        self.assertTrue(boat.is_flying)

    def test_TC_16_wrong_mode_raises_and_keeps_state(self):
        boat = make()
        with self.assertRaises(BoatWrongMode):
            boat.move(10, "air")
        self.assertEqual(boat.energy, 100)
        self.assertEqual(boat.position_km, 0)

    def test_TC_17_zero_distance_raises_value_error(self):
        boat = make()
        with self.assertRaises(ValueError):
            boat.move(0, "water")

    def test_TC_18_unknown_terrain_raises_value_error(self):
        boat = make()
        with self.assertRaises(ValueError):
            boat.move(10, "space")

    def test_TC_19_not_enough_energy_raises_and_keeps_state(self):
        boat = make(energy=5)
        with self.assertRaises(BoatOutOfEnergy):
            boat.move(10, "water")
        self.assertEqual(boat.energy, 5)
        self.assertEqual(boat.position_km, 0)

    def test_TC_20_energy_exactly_enough_gives_zero(self):
        boat = make(energy=10)
        hours = boat.move(10, "water")
        self.assertAlmostEqual(hours, 0.2)
        self.assertEqual(boat.energy, 0)
        self.assertEqual(boat.position_km, 10)

    def test_TC_21_heavy_boat_sinks_and_keeps_state(self):
        boat = make(mass_kg=2000, hull_volume_m3=1)
        with self.assertRaises(BoatSinks):
            boat.move(10, "water")
        self.assertEqual(boat.energy, 100)
        self.assertEqual(boat.position_km, 0)

    def test_TC_22_mass_equal_to_buoyancy_still_floats(self):
        boat = make(mass_kg=1000, hull_volume_m3=1)
        hours = boat.move(10, "water")
        self.assertAlmostEqual(hours, 0.2)
        self.assertEqual(boat.position_km, 10)


class TestCalculateEnergy(unittest.TestCase):
    def test_TC_23_calculate_energy_does_not_change_state(self):
        boat = make()
        cost = boat.calculate_energy(10, "ground")
        self.assertEqual(cost, 15)
        self.assertEqual(boat.energy, 100)
        self.assertEqual(boat.position_km, 0)

    def test_TC_24_unknown_terrain_raises_value_error(self):
        boat = make()
        with self.assertRaises(ValueError):
            boat.calculate_energy(10, "space")


class TestCanOvercome(unittest.TestCase):
    def test_TC_25_wall_in_air_is_passable(self):
        boat = make()
        boat.switch_mode("air")
        self.assertTrue(boat.can_overcome("wall"))

    def test_TC_26_wall_on_water_is_not_passable(self):
        boat = make()
        self.assertFalse(boat.can_overcome("wall"))

    def test_TC_27_river_on_ground_is_not_passable(self):
        boat = make()
        boat.switch_mode("ground")
        self.assertFalse(boat.can_overcome("river"))

    def test_TC_28_unknown_obstacle_raises_value_error(self):
        boat = make()
        with self.assertRaises(ValueError):
            boat.can_overcome("mountain")


class TestRefuel(unittest.TestCase):
    def test_TC_29_refuel_is_capped_at_100(self):
        boat = make(energy=50)
        boat.refuel(80)
        self.assertEqual(boat.energy, 100)

    def test_TC_30_zero_amount_raises_value_error(self):
        boat = make(energy=50)
        with self.assertRaises(ValueError):
            boat.refuel(0)


# ---------------------------------------------------------------------------
# Сценарные тесты (GWT)
# ---------------------------------------------------------------------------

class TestScenarios(unittest.TestCase):
    def test_TC_31_landing_on_the_shore(self):
        # Given: свежая автовертолодка в воде
        pilot = Pilot(make())
        # When: плывёт 10 км, переключается на землю, едет 20 км
        pilot.sail(10)
        self.assertAlmostEqual(pilot.last_hours, 0.2)
        self.assertEqual(pilot.vehicle.energy, 90)
        pilot.switch("ground")
        self.assertEqual(pilot.vehicle.energy, 85)
        pilot.drive(20)
        # Then
        self.assertAlmostEqual(pilot.last_hours, 0.25)
        self.assertEqual(pilot.vehicle.position_km, 30)
        self.assertEqual(pilot.vehicle.energy, 55)
        self.assertEqual(pilot.vehicle.mode, "ground")

    def test_TC_32_flight_over_the_wall(self):
        # Given
        pilot = Pilot(make())
        # When
        pilot.switch("air")
        self.assertTrue(pilot.vehicle.is_flying)
        self.assertEqual(pilot.vehicle.energy, 90)
        self.assertTrue(pilot.vehicle.can_overcome("wall"))
        pilot.fly(20)
        self.assertAlmostEqual(pilot.last_hours, 0.2)
        self.assertEqual(pilot.vehicle.energy, 30)
        pilot.switch("water")
        # Then
        self.assertFalse(pilot.vehicle.is_flying)
        self.assertFalse(pilot.vehicle.can_overcome("wall"))
        self.assertEqual(pilot.vehicle.position_km, 20)
        self.assertEqual(pilot.vehicle.energy, 28)
        self.assertEqual(pilot.vehicle.mode, "water")

    def test_TC_33_sunken_boat_escapes_by_land(self):
        # Given: корпус держит 400 кг, масса 500 кг
        pilot = Pilot(make(hull_volume_m3=0.4))
        # When: пытается плыть
        with self.assertRaises(BoatSinks):
            pilot.sail(5)
        self.assertEqual(pilot.vehicle.position_km, 0)
        self.assertEqual(pilot.vehicle.energy, 100)
        # When: уезжает по земле
        pilot.switch("ground")
        self.assertEqual(pilot.vehicle.energy, 95)
        pilot.drive(10)
        # Then
        self.assertAlmostEqual(pilot.last_hours, 0.125)
        self.assertEqual(pilot.vehicle.position_km, 10)
        self.assertEqual(pilot.vehicle.energy, 80)

    def test_TC_34_out_of_energy_before_takeoff(self):
        # Given
        pilot = Pilot(make(energy=12))
        # When: взлетает, но на полёт энергии нет
        pilot.switch("air")
        self.assertEqual(pilot.vehicle.energy, 2)
        with self.assertRaises(BoatOutOfEnergy):
            pilot.fly(1)
        self.assertEqual(pilot.vehicle.energy, 2)
        self.assertEqual(pilot.vehicle.position_km, 0)
        # When: заправляется и летит
        pilot.vehicle.refuel(50)
        self.assertEqual(pilot.vehicle.energy, 52)
        pilot.fly(1)
        # Then
        self.assertAlmostEqual(pilot.last_hours, 0.01)
        self.assertEqual(pilot.vehicle.energy, 49)
        self.assertEqual(pilot.vehicle.position_km, 1)

    def test_TC_35_full_circle(self):
        # Given
        pilot = Pilot(make())
        # When: воздух -> земля -> вода
        pilot.switch("air")
        pilot.fly(10)
        self.assertEqual(pilot.vehicle.energy, 60)
        pilot.switch("ground")
        pilot.drive(10)
        self.assertEqual(pilot.vehicle.energy, 40)
        pilot.switch("water")
        self.assertEqual(pilot.vehicle.energy, 38)
        pilot.sail(20)
        # Then
        self.assertAlmostEqual(pilot.last_hours, 0.4)
        self.assertTrue(pilot.vehicle.can_overcome("river"))
        status = pilot.vehicle.get_status()
        self.assertEqual(status["name"], "Автовертолодка")
        self.assertEqual(status["energy"], 18)
        self.assertEqual(status["position_km"], 40)
        self.assertEqual(status["mode"], "water")
        self.assertFalse(status["is_flying"])
        self.assertEqual(status["hull_volume_m3"], 1)

    def test_TC_36_forest_and_river(self):
        # Given: свежая автовертолодка (режим water)
        pilot = Pilot(make())
        # When / Then: проходимость в каждом режиме
        expected = {
            "water": {"river": True, "tree": False, "wall": False},
            "ground": {"river": False, "tree": True, "wall": False},
            "air": {"river": True, "tree": True, "wall": True},
        }
        for mode, obstacles in expected.items():
            pilot.switch(mode)
            for obstacle, passable in obstacles.items():
                with self.subTest(mode=mode, obstacle=obstacle):
                    self.assertEqual(
                        pilot.vehicle.can_overcome(obstacle), passable
                    )


if __name__ == "__main__":
    unittest.main()
