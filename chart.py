import csv

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

if __name__ == "__main__":
    file_path = 'cpu_temp_log.csv'
    num_data_points = 20
    last_20_data = fetch_last_n_data_points(file_path, num_data_points)

    if last_20_data:
        print(f"Last {num_data_points} data points from '{file_path}':")
        for row in last_20_data:
            print(f"Timestamp: {row['Timestamp']}, CPU Temp: {row['CPU_Temp_C']}°C")
    else:
        print("No data fetched or an error occurred.")
