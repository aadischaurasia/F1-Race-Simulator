import pygame
import math
import time
import csv
import os

pygame.init()

WIDTH, HEIGHT = 1100, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("F1 Race Simulator - V1.7")

clock = pygame.time.Clock()

# ============================================================
# CAR PARAMETERS
# ============================================================

mass = 800
fuel_mass = 100
engine_force = 9000
brake_force = 14000

rolling_resistance = 120
drag_coefficient = 0.35
frontal_area = 1.5
air_density = 1.225

max_speed = 95

tyre_grip = 1.6
gravity = 9.81
# ===============================
# V1.7 TYRE + FUEL SYSTEM
# ===============================

# V1.9 TYRE COMPOUND SYSTEM

fuel = 100.0
tyre_wear = 0.0

# Current tyre compound
tyre_compound = "Medium"

# Tyre compound properties
tyre_compounds = {
    "Soft": {
        "base_grip": 1.75,
        "min_grip": 1.20,
        "wear_rate": 0.0012
    },

    "Medium": {
        "base_grip": 1.60,
        "min_grip": 1.15,
        "wear_rate": 0.0008
    },

    "Hard": {
        "base_grip": 1.50,
        "min_grip": 1.10,
        "wear_rate": 0.0005
    }
}

fuel_consumption_rate = 0.002
# ============================================================
# GEARBOX
# ============================================================

gears = {
    1: 2.80,
    2: 2.10,
    3: 1.65,
    4: 1.35,
    5: 1.15,
    6: 1.00,
    7: 0.88,
    8: 0.78
}

final_drive = 3.4

gear = 1

idle_rpm = 3000
max_rpm = 15000

wheel_radius = 0.33

# ============================================================
# TRACK
# ============================================================

track_points = [
    (150, 150),
    (400, 120),
    (700, 120),
    (900, 180),
    (930, 300),
    (850, 400),
    (700, 450),
    (850, 550),
    (900, 650),
    (650, 650),
    (400, 620),
    (180, 650),
    (100, 550),
    (160, 430),
    (280, 400),
    (180, 300),
    (120, 220)
]

track_width = 90

start_line = track_points[0]

sector_1_index = 4
sector_2_index = 9
# ============================================
# V2.0 PIT LANE
# ============================================

pit_lane = pygame.Rect(
    180,
    40,
    500,
    70
)

pit_box = pygame.Rect(
    400,
    50,
    80,
    50
)

# ============================================================
# CAR STATE
# ============================================================

x, y = start_line

speed = 0.0
angle = 0.0
# ============================================
# V2.0 PIT STOP
# ============================================

pit_stopping = False
pit_stop_time = 5.0
pit_timer = 0.0
pit_stop_ready = True
pit_target_compound = tyre_compound

throttle = 0.0
brake = 0.0

# ============================================================
# LAP DATA
# ============================================================

lap = 1

lap_start_time = time.time()

current_lap_time = 0
best_lap = None

current_sector = 1

previous_nearest_index = 0

# ============================================================
# TELEMETRY
# ============================================================

telemetry_data = []

simulation_start = time.time()

# ============================================================
# FUNCTIONS
# ============================================================

def calculate_rpm(speed, gear):

    if speed < 0.1:
        return idle_rpm

    wheel_rpm = (
        speed /
        (2 * math.pi * wheel_radius)
    ) * 60

    rpm = wheel_rpm * gears[gear] * final_drive

    return max(
        idle_rpm,
        min(rpm, max_rpm)
    )


def calculate_gear(rpm, gear):

    if rpm > 13500 and gear < 8:
        gear += 1

    elif rpm < 6000 and gear > 1:
        gear -= 1

    return gear


def distance_to_point(px, py, point):

    return math.sqrt(
        (px - point[0]) ** 2 +
        (py - point[1]) ** 2
    )


def nearest_track_point():

    nearest_index = 0
    nearest_distance = float("inf")

    for i, point in enumerate(track_points):

        distance = distance_to_point(
            x,
            y,
            point
        )

        if distance < nearest_distance:

            nearest_distance = distance
            nearest_index = i

    return nearest_index, nearest_distance


def format_time(seconds):

    minutes = int(seconds // 60)

    secs = seconds % 60

    return f"{minutes}:{secs:05.2f}"


def save_telemetry():

    os.makedirs("data", exist_ok=True)

    file_path = "data/telemetry.csv"

    with open(
        file_path,
        "w",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "time",
            "lap",
            "sector",
            "speed_kmh",
            "throttle",
            "brake",
            "rpm",
            "gear",
            "acceleration",
            "fuel",
            "tyre_wear",
            "x",
            "y"
        ])

        writer.writerows(telemetry_data)

    print()
    print("Telemetry saved!")
    print("File:", file_path)
    print("Samples:", len(telemetry_data))


# ============================================================
# MAIN LOOP
# ============================================================

running = True

while running:

    dt = clock.tick(60) / 1000

    # --------------------------------------------------------
    # EVENTS
    # --------------------------------------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_1:
                tyre_compound = "Soft"

            elif event.key == pygame.K_2:
                tyre_compound = "Medium"

            elif event.key == pygame.K_3:
                tyre_compound = "Hard"

    keys = pygame.key.get_pressed()

    # --------------------------------------------------------
    # INPUT
    # --------------------------------------------------------

    throttle = (
        1.0
        if keys[pygame.K_w]
        else 0.0
    )

    brake = (
        1.0
        if keys[pygame.K_s]
        else 0.0
    )

    # --------------------------------------------------------
    # ENGINE / GEARBOX
    # --------------------------------------------------------

    rpm = calculate_rpm(
        speed,
        gear
    )

    gear = calculate_gear(
        rpm,
        gear
    )

    rpm = calculate_rpm(
        speed,
        gear
    )

    rpm_factor = 1.0

    if rpm < 5000:
        rpm_factor = 0.75

    elif rpm > 13000:
        rpm_factor = 0.80

    engine = (
        engine_force *
        throttle *
        rpm_factor
    )

    # --------------------------------------------------------
    # TYRE GRIP
    # --------------------------------------------------------

# Get properties of the current tyre compound
    compound = tyre_compounds[tyre_compound]

    base_grip = compound["base_grip"]
    min_grip = compound["min_grip"]

# Grip decreases as the tyres wear
    tyre_grip = base_grip - (
    tyre_wear / 100
    ) * (base_grip - min_grip)

    maximum_tyre_force = (
    tyre_grip *
    mass *
    gravity
)

    engine = min(
        engine,
        maximum_tyre_force
    )

    braking = brake_force * brake

    braking = min(
        braking,
        maximum_tyre_force
    )

    # --------------------------------------------------------
    # AERODYNAMICS
    # --------------------------------------------------------

    drag = (
        0.5 *
        air_density *
        drag_coefficient *
        frontal_area *
        speed ** 2
    )

    rolling = (
        rolling_resistance
        if speed > 0
        else 0
    )

    # --------------------------------------------------------
    # PHYSICS
    # --------------------------------------------------------

    net_force = (
        engine
        - braking
        - drag
        - rolling
    )

    # V1.8 Fuel Load Physics

    current_fuel_mass = fuel_mass * (fuel / 100)

    total_mass = mass + current_fuel_mass

    acceleration = (
    net_force / total_mass
    )
    # --------------------------------------------------------
    # V1.7 FUEL CONSUMPTION
    # --------------------------------------------------------

    fuel -= (
        throttle *
        fuel_consumption_rate *
        dt
    )

    fuel = max(0.0, fuel)

    # --------------------------------------------------------
    # V1.7 TYRE WEAR
    # --------------------------------------------------------

    # Tyre wear depends on the selected compound
    tyre_wear_rate = compound["wear_rate"]

    tyre_wear += (
    abs(acceleration) *
    tyre_wear_rate *
    dt
    + throttle * 0.0002 * dt
    )

    tyre_wear = min(100.0, tyre_wear)

    speed += acceleration * dt

    speed = max(0, speed)

    speed = min(
        speed,
        max_speed
    )

    # --------------------------------------------------------
    # STEERING
    # --------------------------------------------------------

    steering_strength = 2.5

    if keys[pygame.K_a] and speed > 0:

        angle += (
            steering_strength *
            (speed / max_speed)
        )

    if keys[pygame.K_d] and speed > 0:

        angle -= (
            steering_strength *
            (speed / max_speed)
        )

    # --------------------------------------------------------
    # POSITION
    # --------------------------------------------------------

    x += (
        math.cos(math.radians(angle))
        * speed
        * dt
        * 2
    )

    y -= (
        math.sin(math.radians(angle))
        * speed
        * dt
        * 2
    )
    # ========================================================
    # V2.0 PIT LANE DETECTION
    # ========================================================

    in_pit_lane = pit_lane.collidepoint(x, y)
    # Detect whether the car is inside the pit box
    in_pit_box = pit_box.collidepoint(x, y)

    # V2.1 BASIC STRATEGY
    if tyre_wear >= 50:
        strategy_message = "CONSIDER PIT"
    else:
        strategy_message = "STAY OUT"

    if in_pit_box and pit_stopping:
        keys = pygame.key.get_pressed()

        if keys[pygame.K_1]:
            pit_target_compound = "Soft"

        if keys[pygame.K_2]:
            pit_target_compound = "Medium"

        if keys[pygame.K_3]:
            pit_target_compound = "Hard"
    # Start pit stop when car is stationary in pit box
    # ========================================================
    # V2.0 PIT STOP
    # ========================================================

    # Start pit stop only if the car is ready
    if (
        in_pit_box
        and speed < 1.0
        and not pit_stopping
        and pit_stop_ready
    ):
        pit_stopping = True
        pit_timer = pit_stop_time
        pit_stop_ready = False
        pit_old_compound = tyre_compound


    # Pit stop countdown
    if pit_stopping:

        pit_timer -= dt

        speed = 0

        if pit_timer <= 0:

            pit_timer = 0
            pit_stopping = False
            pit_old_compound = tyre_compound

            # New tyres after pit stop
            tyre_wear = 0.0
            tyre_compound = pit_target_compound

    # Allow another pit stop only after leaving the pit box
    if not in_pit_box:
        pit_stop_ready = True

    # --------------------------------------------------------
    # TRACK PROGRESS
    # --------------------------------------------------------

    nearest_index, nearest_distance = (
        nearest_track_point()
    )

    # --------------------------------------------------------
    # LAP DETECTION
    # --------------------------------------------------------

    if (
        previous_nearest_index
        > len(track_points) - 3
        and nearest_index < 2
        and speed > 2
    ):

        current_lap_time = (
            time.time()
            - lap_start_time
        )

        if lap > 1:

            if (
                best_lap is None
                or current_lap_time < best_lap
            ):

                best_lap = (
                    current_lap_time
                )

        lap += 1

        lap_start_time = time.time()

        current_sector = 1

    # --------------------------------------------------------
    # SECTOR DETECTION
    # --------------------------------------------------------

    if (
        nearest_index >= sector_1_index
        and current_sector == 1
    ):

        current_sector = 2

    if (
        nearest_index >= sector_2_index
        and current_sector == 2
    ):

        current_sector = 3

    previous_nearest_index = (
        nearest_index
    )

    current_lap_time = (
        time.time()
        - lap_start_time
    )

    # ========================================================
    # RECORD TELEMETRY
    # ========================================================

    simulation_time = (
        time.time()
        - simulation_start
    )

    telemetry_data.append([
        round(simulation_time, 3),
        lap,
        current_sector,
        round(speed * 3.6, 2),
        round(throttle * 100, 1),
        round(brake * 100, 1),
        round(rpm, 0),
        gear,
        round(acceleration, 3),
        round(fuel, 2),
        round(tyre_wear, 2),
        round(x, 2),
        round(y, 2)
    ])

    # ========================================================
    # DRAW
    # ========================================================

    screen.fill(
        (25, 80, 35)
    )

    # Track

    pygame.draw.lines(
        screen,
        (80, 80, 80),
        True,
        track_points,
        track_width
    )

    pygame.draw.lines(
        screen,
        (230, 230, 230),
        True,
        track_points,
        3
    )
    # V2.0 Pit Lane

    pygame.draw.rect(
    screen,
    (60, 60, 60),
    pit_lane
    )

    pygame.draw.rect(
    screen,
    (255, 255, 255),
    pit_box,
    2
    )

    # Start / finish

    pygame.draw.line(
        screen,
        (255, 255, 255),
        (
            start_line[0],
            start_line[1] - 40
        ),
        (
            start_line[0],
            start_line[1] + 40
        ),
        5
    )

    # Sector markers

    for index in [
        sector_1_index,
        sector_2_index
    ]:

        px, py = track_points[index]

        pygame.draw.circle(
            screen,
            (255, 200, 0),
            (px, py),
            8
        )

    # --------------------------------------------------------
    # CAR
    # --------------------------------------------------------

    car_length = 34
    car_width = 14

    car = pygame.Surface(
        (
            car_length,
            car_width
        ),
        pygame.SRCALPHA
    )

    pygame.draw.rect(
        car,
        (220, 30, 30),
        (
            0,
            0,
            car_length,
            car_width
        )
    )

    rotated_car = (
        pygame.transform.rotate(
            car,
            angle
        )
    )

    screen.blit(
        rotated_car,
        rotated_car.get_rect(
            center=(x, y)
        )
    )

    # ========================================================
    # TELEMETRY DISPLAY
    # ========================================================

    font = pygame.font.Font(
        None,
        27
    )

    speed_kmh = speed * 3.6

    telemetry = [

        f"Speed       : {speed_kmh:6.1f} km/h",

        f"Throttle    : {throttle * 100:6.0f} %",

        f"Brake       : {brake * 100:6.0f} %",

        f"RPM         : {rpm:6.0f}",

        f"Gear        : {gear}",

        f"Acceleration: {acceleration:6.2f} m/s²",
        f"Pit Lane    : {'YES' if in_pit_lane else 'NO'}",
        f"Pit Box     : {'YES' if in_pit_box else 'NO'}",
        f"Pit Stop    : {'YES' if pit_stopping else 'NO'}",
        f"Pit Timer   : {pit_timer:4.1f} s",
        f"Fuel        : {fuel:6.1f} %",
        f"Tyre Compound : {tyre_compound}",
        f"Pit Target  : {pit_target_compound}", 
        f"Tyre Wear   : {tyre_wear:6.1f} %",
        f"Strategy    : {strategy_message}",
        f"Vehicle Mass:{total_mass:.1f} kg",

        "",

        f"Lap         : {lap}",

        f"Lap Time    : "
        f"{format_time(current_lap_time)}",

        f"Best Lap    : "
        + (
            "--:--.--"
            if best_lap is None
            else format_time(best_lap)
        ),

        "",

        f"Sector      : {current_sector}"

    ]

    for i, text in enumerate(
        telemetry
    ):

        surface = font.render(
            text,
            True,
            (255, 255, 255)
        )

        screen.blit(
            surface,
            (
                20,
                20 + i * 25
            )
        )
    pygame.display.flip()

# ============================================================
# SAVE TELEMETRY WHEN PROGRAM CLOSES
# ============================================================

save_telemetry()

pygame.quit()