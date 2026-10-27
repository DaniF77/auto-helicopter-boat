# DEMO: Автовертолодка

1. Запустить тесты из корня проекта: `python -m unittest discover -s tests -v`. Ожидаем `Ran 36 tests`, `OK`.
2. Показать транспорт в работе:

```python
from auto_helicopter_boat import AutoHelicopterBoat

boat = AutoHelicopterBoat("Амфибиус", mass_kg=500, hull_volume_m3=1, max_speed_kmh=100)
print(boat.move(10, "water"))      # 0.2 ч, энергия 90
boat.switch_mode("ground")         # энергия 85
print(boat.move(20, "ground"))     # 0.25 ч, энергия 55
boat.switch_mode("air")            # энергия 45
print(boat.can_overcome("wall"))   # True
print(boat.get_status())
```

3. Показать утонувшую лодку: `AutoHelicopterBoat("Тяжёлая", 2000, 1, 100).move(10, "water")` даёт `BoatSinks`.
