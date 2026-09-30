# Test Case Specification: «Автовертолодка»

Ссылка на тест в артефактах — это ID из этих таблиц. Источник — раздел `SPEC.md`.

Если не указано иное: `mass_kg=500`, `hull_volume_m3=1`, `max_speed_kmh=100`, `energy=100`, режим `"water"`.

Соотношение: 30 модульных и 6 сценарных (≈ 83 / 17).

## Модульные тесты

| ID | Источник | Предусловие | Вход | Ожидание | Приоритет |
|---|---|---|---|---|---|
| TC-01 | SPEC 3.2 | — | `name=""` | `ValueError` | high |
| TC-02 | SPEC 3.2 | — | `mass_kg=0` | `ValueError` | high |
| TC-03 | SPEC 3.2 | — | `hull_volume_m3=-1` | `ValueError` | high |
| TC-04 | SPEC 3.2 | — | `max_speed_kmh=0` | `ValueError` | high |
| TC-05 | SPEC 3.2 | — | `energy=101` | `ValueError` | high |
| TC-06 | SPEC 3.2 | — | `energy=-1` | `ValueError` | medium |
| TC-07 | SPEC 3.2 | — | конструктор без `energy` | `energy=100`, `mode="water"`, `position_km=0`, `is_flying=False` | high |
| TC-08 | SPEC 3.4.1 | режим `"water"` | `switch_mode("ground")` | `mode="ground"`, `energy=95`, `is_flying=False` | high |
| TC-09 | SPEC 3.4.1 | режим `"water"` | `switch_mode("air")` | `mode="air"`, `energy=90`, `is_flying=True` | high |
| TC-10 | SPEC 3.4.1 | — | `switch_mode("space")` | `ValueError` | high |
| TC-11 | SPEC 3.4.1, 5 | режим `"water"` | `switch_mode("water")` | `energy=100`, `mode="water"` | medium |
| TC-12 | SPEC 3.4.1 | `energy=4` | `switch_mode("ground")` | `BoatOutOfEnergy`, `mode="water"`, `energy=4` | high |
| TC-13 | SPEC 3.4.2 | режим `"water"` | `move(10, "water")` | возвращает 0.2, `energy=90`, `position_km=10` | high |
| TC-14 | SPEC 3.4.2 | режим `"ground"` (после `switch_mode`, `energy=95`) | `move(40, "ground")` | возвращает 0.5, `energy=35`, `position_km=40` | high |
| TC-15 | SPEC 3.4.2 | режим `"air"` (после `switch_mode`, `energy=90`) | `move(10, "air")` | возвращает 0.1, `energy=60`, `position_km=10`, `is_flying=True` | high |
| TC-16 | SPEC 3.4.2 | режим `"water"` | `move(10, "air")` | `BoatWrongMode`, `energy=100`, `position_km=0` | high |
| TC-17 | SPEC 3.4.2 | режим `"water"` | `move(0, "water")` | `ValueError` | high |
| TC-18 | SPEC 3.4.2 | режим `"water"` | `move(10, "space")` | `ValueError` | high |
| TC-19 | SPEC 3.4.2 | `energy=5` | `move(10, "water")` | `BoatOutOfEnergy`, `energy=5`, `position_km=0` | high |
| TC-20 | SPEC 3.4.2, 5 | `energy=10` | `move(10, "water")` | возвращает 0.2, `energy=0`, `position_km=10` | medium |
| TC-21 | SPEC 3.4.2 | `mass_kg=2000`, `hull_volume_m3=1` | `move(10, "water")` | `BoatSinks`, `energy=100`, `position_km=0` | high |
| TC-22 | SPEC 3.4.2, 5 | `mass_kg=1000`, `hull_volume_m3=1` | `move(10, "water")` | возвращает 0.2, `position_km=10` (не тонет) | medium |
| TC-23 | SPEC 3.4.3 | режим `"water"` | `calculate_energy(10, "ground")` | возвращает 15, `energy=100`, `position_km=0` | high |
| TC-24 | SPEC 3.4.3 | — | `calculate_energy(10, "space")` | `ValueError` | medium |
| TC-25 | SPEC 3.4.4 | режим `"air"` | `can_overcome("wall")` | `True` | high |
| TC-26 | SPEC 3.4.4 | режим `"water"` | `can_overcome("wall")` | `False` | high |
| TC-27 | SPEC 3.4.4 | режим `"ground"` | `can_overcome("river")` | `False` | high |
| TC-28 | SPEC 3.4.4 | — | `can_overcome("mountain")` | `ValueError` | medium |
| TC-29 | SPEC 3.4.5, 5 | `energy=50` | `refuel(80)` | `energy=100` | high |
| TC-30 | SPEC 3.4.5 | `energy=50` | `refuel(0)` | `ValueError` | medium |

## Сценарные тесты

| ID | Источник | Вход | Ожидание | Приоритет |
|---|---|---|---|---|
| TC-31 | SPEC 4.1 | шаги 1–3 сценария «Высадка на берег» | `position_km=30`, `energy=55`, `mode="ground"` | high |
| TC-32 | SPEC 4.2 | шаги 1–5 сценария «Полёт через стену» | `position_km=20`, `energy=28`, `mode="water"` | high |
| TC-33 | SPEC 4.3 | шаги 1–3 сценария «Утонувшая автовертолодка» | `position_km=10`, `energy=80`, первое движение — `BoatSinks` | high |
| TC-34 | SPEC 4.4 | шаги 1–4 сценария «Не хватило энергии на взлёт» | `position_km=1`, `energy=49`, второй `move` — `BoatOutOfEnergy` | high |
| TC-35 | SPEC 4.5 | шаги 1–5 сценария «Полный круг» | `position_km=40`, `energy=18`, `mode="water"`, `get_status()` совпадает | medium |
| TC-36 | SPEC 4.6 | сценарий «Лес и река» | таблица проходимости совпадает со SPEC 4.6 | medium |
