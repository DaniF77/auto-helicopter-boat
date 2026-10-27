"""Модель трёхрежимного транспорта: лодки, автомобиля и вертолёта."""


class BoatSinks(Exception):
    """Вызывается, когда корпус не удерживает массу на воде."""

    def __init__(self, message: str = "Автовертолодка тонет.") -> None:
        super().__init__(message)
        print(message)


class BoatWrongMode(Exception):
    """Вызывается при попытке двигаться не в текущем режиме."""

    def __init__(self, message: str = "Выбран неверный режим движения.") -> None:
        super().__init__(message)
        print(message)


class BoatOutOfEnergy(Exception):
    """Вызывается, когда запаса энергии недостаточно для действия."""

    def __init__(self, message: str = "Недостаточно энергии.") -> None:
        super().__init__(message)
        print(message)


class AutoHelicopterBoat:
    """Автовертолодка с режимами движения по воде, земле и воздуху."""

    _MODES = {
        "water": (0.5, 1, 2),
        "ground": (0.8, 1.5, 5),
        "air": (1.0, 3, 10),
    }
    _OBSTACLES = {"wall", "river", "tree"}

    def __init__(
        self,
        name: str,
        mass_kg: float,
        hull_volume_m3: float,
        max_speed_kmh: float,
        energy: float = 100.0,
    ) -> None:
        """Создать транспорт с полным или указанным запасом энергии."""
        if not name.strip():
            raise ValueError("Name must not be empty")
        if mass_kg <= 0 or hull_volume_m3 <= 0 or max_speed_kmh <= 0:
            raise ValueError("Mass, hull volume and speed must be positive")
        if not 0 <= energy <= 100:
            raise ValueError("Energy must be between 0 and 100")

        self.name = name
        self.mass_kg = mass_kg
        self.hull_volume_m3 = hull_volume_m3
        self.max_speed_kmh = max_speed_kmh
        self.energy = energy
        self.position_km = 0
        self.mode = "water"

    @property
    def is_flying(self) -> bool:
        """Вернуть, находится ли транспорт в воздушном режиме."""
        return self.mode == "air"

    def switch_mode(self, new_mode: str) -> None:
        """Переключить режим, списав стоимость нового режима."""
        if new_mode not in self._MODES:
            raise ValueError("Unknown mode")
        if new_mode == self.mode:
            return

        switch_cost = self._MODES[new_mode][2]
        if self.energy < switch_cost:
            raise BoatOutOfEnergy("Not enough energy to switch mode")

        self.energy -= switch_cost
        self.mode = new_mode

    def move(self, distance_km: float, terrain: str) -> float:
        """Переместиться и вернуть затраченное на путь время в часах."""
        if distance_km <= 0:
            raise ValueError("Distance must be positive")
        if terrain not in self._MODES:
            raise ValueError("Unknown terrain")
        if terrain != self.mode:
            raise BoatWrongMode("Terrain does not match the current mode")
        if terrain == "water" and self.mass_kg > self.hull_volume_m3 * 1000:
            raise BoatSinks("The boat sinks")

        speed_factor, energy_per_km, _ = self._MODES[terrain]
        energy_cost = distance_km * energy_per_km
        if self.energy < energy_cost:
            raise BoatOutOfEnergy("Not enough energy to move")

        self.energy -= energy_cost
        self.position_km += distance_km
        return distance_km / (self.max_speed_kmh * speed_factor)

    def calculate_energy(self, distance_km: float, terrain: str) -> float:
        """Рассчитать расход энергии для пути, не меняя состояние."""
        if distance_km <= 0:
            raise ValueError("Distance must be positive")
        if terrain not in self._MODES:
            raise ValueError("Unknown terrain")
        return distance_km * self._MODES[terrain][1]

    def can_overcome(self, obstacle: str) -> bool:
        """Вернуть возможность преодолеть препятствие в текущем режиме."""
        if obstacle not in self._OBSTACLES:
            raise ValueError("Unknown obstacle")

        if obstacle == "wall":
            return self.mode == "air"
        if obstacle == "river":
            return self.mode in ("water", "air")
        return self.mode in ("ground", "air")

    def refuel(self, amount: float) -> None:
        """Пополнить энергию, не превышая максимума в 100 единиц."""
        if amount <= 0:
            raise ValueError("Fuel amount must be positive")
        self.energy = min(100, self.energy + amount)

    def get_status(self) -> dict:
        """Вернуть снимок текущего состояния транспорта."""
        return {
            "name": self.name,
            "energy": self.energy,
            "position_km": self.position_km,
            "mode": self.mode,
            "is_flying": self.is_flying,
            "hull_volume_m3": self.hull_volume_m3,
        }
