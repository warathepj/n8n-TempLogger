import subprocess
import time
import datetime

LOG_FILE = "cpu_temp_log.csv"
INTERVAL = 5  # seconds

def get_cpu_temp():
    try:
        # Run the sensors command and capture output
        result = subprocess.run(['sensors'], capture_output=True, text=True, check=True)
        output = result.stdout

        # Parse the output to find CPU temperature (adjust regex if needed)
        for line in output.splitlines():
            if 'Package id 0:' in line:
                parts = line.split()
                # Assuming the temperature is the 4th part, e.g., "+45.0°C"
                if len(parts) > 3:
                    temp_str = parts[3].replace('+', '').replace('°C', '')
                    try:
                        return float(temp_str)
                    except ValueError:
                        return None
        return None
    except Exception as e:
        print(f"Error getting CPU temperature: {e}")
        return None

def main():
    print(f"Logging CPU temperature every {INTERVAL} seconds. Press Ctrl+C to stop.")
    with open(LOG_FILE, 'a') as f:
        # Write header if file is new or empty
        if f.tell() == 0:
            f.write("Timestamp,CPU_Temp_C\n")

        while True:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cpu_temp = get_cpu_temp()

            if cpu_temp is not None:
                log_entry = f"{timestamp},{cpu_temp}\n"
                f.write(log_entry)
                print(f"Logged: {log_entry.strip()}")
            else:
                print(f"Logged: {timestamp},Could not read temp") # Log if temp couldn't be read

            time.sleep(INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nLogging stopped by user.")