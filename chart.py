import csv
import matplotlib.pyplot as plt
from datetime import datetime

def fetch_last_n_data_points(file_path, n):
    """
    Fetches the last n data points from a CSV file.

    Args:
        file_path (str): The path to the CSV file.
        n (int): The number of data points to fetch from the end of the file.

    Returns:
        list: A list of dictionaries, where each dictionary represents a row
              with 'Timestamp' and 'CPU_Temp_C' keys, or an empty list if an error occurs.
    """
    try:
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            data = list(reader)
            return data[-n:]
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def create_cpu_temp_chart(data, output_filename="cpu_temp_chart.png"):
    """
    Creates and saves a line chart of CPU temperature over time.

    Args:
        data (list): A list of dictionaries containing 'Timestamp' and 'CPU_Temp_C'.
        output_filename (str): The name of the file to save the chart to.
    """
    if not data:
        print("No data to plot.")
        return

    timestamps = [datetime.strptime(row['Timestamp'], '%Y-%m-%d %H:%M:%S') for row in data]
    cpu_temps = [float(row['CPU_Temp_C']) for row in data]

    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, cpu_temps, marker='o', linestyle='-', color='b')
    plt.title('Last 20 CPU Temperature Readings')
    plt.xlabel('Timestamp')
    plt.ylabel('CPU Temperature (°C)')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout() # Adjust layout to prevent labels from overlapping
    plt.savefig(output_filename)
    print(f"Chart saved as '{output_filename}'")
    plt.show() # Display the chart

if __name__ == "__main__":
    file_path = 'cpu_temp_log.csv'
    num_data_points = 20
    last_20_data = fetch_last_n_data_points(file_path, num_data_points)

    if last_20_data:
        print(f"Last {num_data_points} data points from '{file_path}':")
        for row in last_20_data:
            print(f"Timestamp: {row['Timestamp']}, CPU Temp: {row['CPU_Temp_C']}°C")
        
        create_cpu_temp_chart(last_20_data)
    else:
        print("No data fetched or an error occurred.")
