import pandas as pd
import matplotlib.pyplot as plt

# Load telemetry
df = pd.read_csv("data/telemetry.csv")

print("\n========== TELEMETRY ==========")
print(df.head())

print("\nColumns:")
print(df.columns.tolist())

print("\n========== RACE STATISTICS ==========")

print(f"Maximum Speed : {df['speed_kmh'].max():.1f} km/h")
print(f"Average Speed : {df['speed_kmh'].mean():.1f} km/h")
print(f"Maximum RPM   : {df['rpm'].max():.0f}")

print(f"Starting Fuel : {df['fuel'].iloc[0]:.1f}%")
print(f"Ending Fuel   : {df['fuel'].iloc[-1]:.1f}%")

print(f"Starting Tyre Wear : {df['tyre_wear'].iloc[0]:.1f}%")
print(f"Ending Tyre Wear   : {df['tyre_wear'].iloc[-1]:.1f}%")

# -------------------------------
# SPEED
# -------------------------------

plt.figure(figsize=(10, 5))
plt.plot(df["time"], df["speed_kmh"])

plt.xlabel("Time (s)")
plt.ylabel("Speed (km/h)")
plt.title("Speed vs Time")
plt.grid()

plt.show()

# -------------------------------
# THROTTLE / BRAKE
# -------------------------------

plt.figure(figsize=(10, 5))

plt.plot(df["time"], df["throttle"], label="Throttle")
plt.plot(df["time"], df["brake"], label="Brake")

plt.xlabel("Time (s)")
plt.ylabel("Input (%)")
plt.title("Throttle and Brake")
plt.legend()
plt.grid()

plt.show()

# -------------------------------
# RPM
# -------------------------------

plt.figure(figsize=(10, 5))

plt.plot(df["time"], df["rpm"])

plt.xlabel("Time (s)")
plt.ylabel("RPM")
plt.title("Engine RPM")
plt.grid()

plt.show()

# -------------------------------
# LAP COMPARISON
# -------------------------------

plt.figure(figsize=(10, 5))

for lap in sorted(df["lap"].unique()):

    lap_data = df[df["lap"] == lap]

    plt.plot(
        lap_data["time"],
        lap_data["speed_kmh"],
        label=f"Lap {int(lap)}"
    )

plt.xlabel("Time (s)")
plt.ylabel("Speed (km/h)")
plt.title("Speed Comparison by Lap")
plt.legend()
plt.grid()

plt.show()

# -------------------------------
# FUEL
# -------------------------------

plt.figure(figsize=(10, 5))

plt.plot(
    df["time"],
    df["fuel"]
)

plt.xlabel("Time (s)")
plt.ylabel("Fuel (%)")
plt.title("Fuel Consumption")
plt.grid()

plt.show()

# -------------------------------
# TYRE WEAR
# -------------------------------

plt.figure(figsize=(10, 5))

plt.plot(
    df["time"],
    df["tyre_wear"]
)

plt.xlabel("Time (s)")
plt.ylabel("Tyre Wear (%)")
plt.title("Tyre Degradation")
plt.grid()

plt.show()

print("\nTelemetry analysis complete.")