import os
import pandas as pd
import matplotlib.pyplot as plt

def plot_sensor_data(input_folder):
    # Create output folder
    output_folder = input_folder + "_plots"
    os.makedirs(output_folder, exist_ok=True)

    # Traverse all CSV files in the folder
    for file in os.listdir(input_folder):
        if file.endswith(".csv"):
            file_path = os.path.join(input_folder, file)

            # Read CSV
            df = pd.read_csv(file_path)

            # Create subplots
            fig, axs = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

            # Plot Accelerometer
            axs[0].plot(df['Accel_X'], label='Accel_X')
            axs[0].plot(df['Accel_Y'], label='Accel_Y')
            axs[0].plot(df['Accel_Z'], label='Accel_Z')
            axs[0].set_title("Accelerometer Data")
            axs[0].set_ylabel("Accel")
            axs[0].legend()
            axs[0].grid(True)

            # Plot Gyroscope
            axs[1].plot(df['Gyro_X'], label='Gyro_X')
            axs[1].plot(df['Gyro_Y'], label='Gyro_Y')
            axs[1].plot(df['Gyro_Z'], label='Gyro_Z')
            axs[1].set_title("Gyroscope Data")
            axs[1].set_xlabel("Sample Index")
            axs[1].set_ylabel("Gyro")
            axs[1].legend()
            axs[1].grid(True)

            # Adjust layout
            plt.tight_layout()

            # Save figure
            output_file = os.path.join(output_folder, file.replace(".csv", ".png"))
            plt.savefig(output_file)
            plt.close()

            print(f"Saved plot: {output_file}")



if __name__ == "__main__":
    folder_name = "mydata"  
    plot_sensor_data(folder_name)
