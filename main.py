import subprocess
import time
import datetime
import requests
from flask import Flask, request, jsonify
import threading
import csv # Added import for csv

LOG_FILE = "cpu_temp_log.csv"
INTERVAL = 500  # seconds
WEBHOOK_URL = "https://d61a62db74d9.ngrok-free.app/webhook-test/d65403f4-08fb-4256-84b1-ab8e3d057988"
app = Flask(__name__)

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

def send_alert_to_webhook(payload): # Changed 'message' to 'payload'
    try:
        # If payload is a string, wrap it in a dictionary for consistency
        if isinstance(payload, str):
            payload = {"message": payload}
        
        response = requests.post(WEBHOOK_URL, json=payload) # Always send as JSON
        response.raise_for_status()
        print(f"Successfully sent alert to webhook: {payload}") # Print the payload sent
        print(f"Webhook response status: {response.status_code}")
        print(f"Webhook response text: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending alert to webhook: {e}")
        if e.response is not None:
            print(f"Webhook error response status: {e.response.status_code}")
            print(f"Webhook error response text: {e.response.text}")

@app.route('/test-webhook', methods=['POST'])
def test_webhook_endpoint():
    test_message = "This is a test message from the dedicated /test-webhook endpoint."
    send_alert_to_webhook(test_message)
    return jsonify({"status": "success", "action": "test_message_sent", "message": test_message}), 200

@app.route('/receive-message', methods=['POST'])
def receive_message_endpoint():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"status": "error", "message": "Invalid request: 'message' field is missing"}), 400
        
        received_message = data['message']
        print(f"Received message: {received_message}")
        
        if received_message == "/log":
            last_n_data = get_last_n_data_points()
            print(f"Last 10 data points from cpu_temp_log.csv: {last_n_data}")
            time.sleep(4) # Wait for 4 seconds
            send_alert_to_webhook({"data_points": last_n_data}) # Send last_n_data to webhook
            return jsonify({"status": "success", "action": "log_data_printed", "data": last_n_data}), 200
        elif received_message == "/chart":
            print("Executing chart.py to generate CPU temperature chart...")
            try:
                subprocess.run(['python3', 'chart.py'], check=True)
                chart_message = "CPU temperature chart generated and saved as 'cpu_temp_chart.png'."
                print(chart_message)
                send_alert_to_webhook({"message": chart_message, "chart_generated": True})
                return jsonify({"status": "success", "action": "chart_generated", "message": chart_message}), 200
            except subprocess.CalledProcessError as e:
                error_message = f"Error executing chart.py: {e}"
                print(error_message)
                send_alert_to_webhook({"message": error_message, "chart_generated": False, "error": str(e)})
                return jsonify({"status": "error", "action": "chart_generation_failed", "message": error_message}), 500
        
        return jsonify({"status": "success", "action": "message_received", "received_message": received_message}), 200
    except Exception as e:
        print(f"Error receiving message: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# def log_cpu_temp_periodically():
#     print(f"Logging CPU temperature every {INTERVAL} seconds. Press Ctrl+C to stop.")
#     with open(LOG_FILE, 'a') as f:
#         # Write header if file is new or empty
#         if f.tell() == 0:
#             f.write("Timestamp,CPU_Temp_C\n")

#         while True:
#             timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             cpu_temp = get_cpu_temp()

#             if cpu_temp is not None:
#                 log_entry = f"{timestamp},{cpu_temp}\n"
#                 f.write(log_entry)
#                 f.flush()  # Ensure data is written to the file immediately
#                 print(f"Logged: {log_entry.strip()}")
#                 if cpu_temp > 60.0:
#                     print("CPU temperature is high!")
#                     # send_alert_to_webhook("hight")
#             else:
#                 print(f"Logged: {timestamp},Could not read temp") # Log if temp couldn't be read

#             time.sleep(INTERVAL)

def get_last_n_data_points(n=10):
    try:
        with open(LOG_FILE, 'r') as f:
            reader = csv.DictReader(f)
            # Read all rows into a list
            rows = list(reader)
            
            # Get the last n rows
            last_n_rows = rows[-n:] if len(rows) >= n else rows
        
        if last_n_rows:
            data_points = []
            for row in last_n_rows:
                try:
                    data_points.append({
                        "timestamp": row.get("Timestamp"),
                        "cpu_temp_c": float(row.get("CPU_Temp_C"))
                    })
                except ValueError:
                    # Handle cases where CPU_Temp_C might not be a valid float
                    continue
            return data_points
        else:
            return {"message": f"No data points found in {LOG_FILE}"}
    except FileNotFoundError:
        return {"message": f"Error: {LOG_FILE} not found."}
    except Exception as e:
        print(f"Error getting last {n} data points: {e}")
        return {"message": f"Error: {str(e)}"}

def send_last_n_data_points_to_webhook():
    last_n_data = get_last_n_data_points()
    if isinstance(last_n_data, list) and last_n_data: # Only send if actual data (list of dicts) is found
        send_alert_to_webhook({"data_points": last_n_data})
    else:
        send_alert_to_webhook(last_n_data) # Send the message if no data or error

# def send_last_data_periodically_6_sec():
#     print(f"Sending last data point to webhook every 6 seconds.")
#     while True:
#         send_last_data_point_to_webhook()
#         time.sleep(6) # Send every 6 seconds

if __name__ == "__main__":
    # Start CPU temperature logging in a separate thread
    # logging_thread = threading.Thread(target=log_cpu_temp_periodically)
    # logging_thread.daemon = True  # Allow the main program to exit even if this thread is running
    # logging_thread.start()

    # Start sending last data point to webhook every 6 seconds in a separate thread
    # send_data_6_sec_thread = threading.Thread(target=send_last_data_periodically_6_sec)
    # send_data_6_sec_thread.daemon = True
    # send_data_6_sec_thread.start()

    # Run the Flask app
    try:
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\nServer and logging stopped by user.")
