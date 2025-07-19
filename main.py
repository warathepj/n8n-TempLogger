import subprocess
import time
import datetime
import requests
from flask import Flask, request, jsonify
import threading

LOG_FILE = "cpu_temp_log.csv"
INTERVAL = 5  # seconds
WEBHOOK_URL = "http://localhost:5678/webhook-test/d65403f4-08fb-4256-84b1-ab8e3d057988"

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

def send_alert_to_webhook(message):
    try:
        payload = {"message": message}
        response = requests.post(WEBHOOK_URL, json=payload)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        print(f"Successfully sent alert to webhook: {message}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending alert to webhook: {e}")

@app.route('/n8n-webhook', methods=['POST'])
def n8n_webhook():
    if request.is_json:
        data = request.get_json()
        message = data.get('message', 'No message provided')
        print(f"Received message from n8n: {message}")
        # You can add more logic here based on the received message
        # For example, trigger an alert or log it
        send_alert_to_webhook(f"Message from n8n: {message}")
        return jsonify({"status": "success", "received_message": message}), 200
    else:
        return jsonify({"status": "error", "message": "Request must be JSON"}), 400

def log_cpu_temp_periodically():
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
                if cpu_temp > 60.0:
                    print("CPU temperature is high!")
                    send_alert_to_webhook("hight")
            else:
                print(f"Logged: {timestamp},Could not read temp") # Log if temp couldn't be read

            time.sleep(INTERVAL)

if __name__ == "__main__":
    # Start CPU temperature logging in a separate thread
    logging_thread = threading.Thread(target=log_cpu_temp_periodically)
    logging_thread.daemon = True  # Allow the main program to exit even if this thread is running
    logging_thread.start()

    # Run the Flask app
    try:
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\nServer and logging stopped by user.")
