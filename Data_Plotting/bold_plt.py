import pandas as pd
import matplotlib.pyplot as plt
import mplcyberpunk

plt.style.use("cyberpunk")



# Step 1: Read data from CSV
df = pd.read_csv('sample3.csv')  # Replace with your file path if needed
lwidth=3.5
# Step 2: Plotting
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

# --- Accelerometer Plot ---
ax1.plot(df['Accel_X'], label='Accel_X', linewidth=lwidth, linestyle='-')
ax1.plot(df['Accel_Y'], label='Accel_Y', linewidth=lwidth, linestyle='--')
ax1.plot(df['Accel_Z'], label='Accel_Z', linewidth=lwidth, linestyle='-.')
ax1.set_title('Accelerometer Data')
ax1.set_ylabel('Acceleration')
ax1.legend()
ax1.grid(True)

# --- Gyroscope Plot ---
ax2.plot(df['Gyro_X'], label='Gyro_X', linewidth=lwidth, linestyle='-')
ax2.plot(df['Gyro_Y'], label='Gyro_Y', linewidth=lwidth, linestyle='--')
ax2.plot(df['Gyro_Z'], label='Gyro_Z', linewidth=lwidth, linestyle='-.')
ax2.set_title('Gyroscope Data')
ax2.set_ylabel('Angular Velocity')
ax2.set_xlabel('Sample Index')
ax2.legend()
# ax2.grid(True)

plt.tight_layout()

mplcyberpunk.add_glow_effects()

plt.show()

