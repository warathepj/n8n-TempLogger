# ซอร์สโค้ดนี้ ใช้สำหรับเป็นตัวอย่างเท่านั้น ถ้านำไปใช้งานจริง ผู้ใช้ต้องจัดการเรื่องความปลอดภัย และ ประสิทธิภาพด้วยตัวเอง

# This app is for Linux only.

# TempLogger: CPU Temperature Monitoring with n8n and Telegram

A system for monitoring CPU temperature, logging data, generating charts, and sending alerts/reports via Telegram using n8n workflows.

## Features:
*   **CPU Temperature Monitoring:** Periodically logs CPU temperature.
*   **High Temperature Alerts:** Sends alerts to Telegram via n8n when CPU temperature exceeds a threshold.
*   **On-Demand Data Logging:** Retrieves and sends recent CPU temperature data points to Telegram upon request.
*   **CPU Temperature Chart Generation:** Generates and serves a visual chart of CPU temperature history.
*   **Telegram Integration:** Interacts with Telegram for alerts, data requests, and chart delivery.
*   **Webhook Communication:** Utilizes webhooks for seamless integration between the Python application and n8n workflows.

## System Architecture/Overview:
*   **`main.py` (Python Application):**
    *   Continuously monitors CPU temperature and logs it to `cpu_temp_log.csv`.
    *   Triggers n8n `TempLogger-alert` webhook for high temperature alerts.
    *   Exposes `/receive-message` endpoint to receive commands from n8n `TempLogger-report` workflow (e.g., `/log` for data, `/chart` for chart generation).
    *   Exposes `/cpu-chart` endpoint to serve the generated chart image.
*   **`chart.py` (Python Script):**
    *   Reads data from `cpu_temp_log.csv`.
    *   Generates a line chart of CPU temperatures and saves it as `cpu_temp_chart.png`.
*   **n8n Workflows:**
    *   **`TempLogger-alert`:** Receives alerts/data from `main.py` via webhook and forwards them to Telegram. Handles high-temp alerts, raw data logging, and chart completion messages.
    *   **`TempLogger-report`:** Receives commands from Telegram (e.g., `/log`, `/chart`) and forwards them to `main.py`'s `/receive-message` endpoint via HTTP request.

## Setup/Installation:
*   **Python Environment:**
    *   Clone the repository.
    *   Install dependencies (e.g., `Flask`, `requests`, `matplotlib`, `psutil` for `sensors` command if not already installed).
    *   Ensure the `sensors` command is available on your system for CPU temperature reading.
*   **n8n Configuration:**
    *   Import `TempLogger-alert` and `TempLogger-report` workflows into your n8n instance.
    *   Configure Telegram credentials in n8n.
    *   Update Telegram Chat ID in `TempLogger-alert` workflow.
    *   Update webhook URL in `main.py` to match your n8n `TempLogger-alert` webhook URL.
    *   Update `https://your-url/receive-message` and `https://your-url/cpu-chart` in n8n workflows to point to your `main.py` application's endpoints.
    *   Activate both n8n workflows.

## Usage:
*   Run `main.py` (e.g., `python3 main.py`).
*   Interact via Telegram:
    *   Receive automatic high-temperature alerts.
    *   Send `/log` to your Telegram bot to get recent temperature data.
    *   Send `/chart` to your Telegram bot to generate and receive a link to the CPU temperature chart.

## File Descriptions:
*   `main.py`: Core Python application for logging, alerting, and API endpoints.
*   `chart.py`: Python script for generating CPU temperature charts.
*   `cpu_temp_log.csv`: CSV file storing CPU temperature logs.
*   `cpu_temp_chart.png`: Generated CPU temperature chart image.
*   `requirements.txt`: Python dependencies.

## Future Improvements:
*   Containerization (Docker).
*   More robust error handling and logging.
*   User interface for chart viewing.
*   Database integration instead of CSV.

# How to use sensors on Linux:

Linux systems, from personal computers to servers, rely heavily on various sensors to monitor hardware health and performance. These sensors can measure CPU temperature, fan speeds, voltage levels, disk activity, network traffic, and more.

Here's a breakdown of how to use sensors on Linux, covering the primary tool and some popular monitoring applications:

## 1\. `lm_sensors` (Linux monitoring sensors)

This is the foundational package for accessing hardware sensor data on most Linux distributions.

**Installation:**

  * **Debian/Ubuntu:** `sudo apt install lm-sensors`
  * **Fedora/RHEL/CentOS:** `sudo dnf install lm_sensors` or `sudo yum install lm_sensors`
  * **Arch Linux:** `sudo pacman -S lm_sensors`

**Configuration and Detection:**

After installation, you need to detect the sensors on your system. This is done with the `sensors-detect` command.

1.  **Run `sensors-detect`:**

    ```bash
    sudo sensors-detect
    ```

    This command will probe your system for available sensor chips. It will ask you a series of questions. For most users, it's generally safe to accept the default answers by pressing Enter at each prompt. You can also use `sudo sensors-detect --auto` to automatically accept all safe answers.

2.  **Load Kernel Modules:**
    `sensors-detect` will suggest which kernel modules (drivers) need to be loaded to enable sensor monitoring. It will often ask if you want to add these modules to `/etc/modules` (or a similar configuration file) so they load automatically on boot. It's recommended to say "yes" to this.

3.  **Restart (Optional, but recommended for some modules):**
    After `sensors-detect` runs, it might recommend a reboot to ensure all detected modules are loaded correctly.

**Reading Sensor Data:**

Once `lm_sensors` is configured, you can simply run the `sensors` command to see the readings:

```bash
sensors
```

This will output a summary of your detected sensors, including:

  * **CPU Core Temperatures:** Often shown as "Core 0," "Core 1," etc.
  * **Motherboard Temperatures:** Various temperature readings from different points on your motherboard.
  * **Fan Speeds:** RPMs of CPU, chassis, and other fans.
  * **Voltages:** Power supply and component voltages.

**Example Output:**

```
coretemp-isa-0000
Adapter: ISA adapter
Package id 0:  +45.0°C  (high = +80.0°C, crit = +100.0°C)
Core 0:        +45.0°C  (high = +80.0°C, crit = +100.0°C)
Core 1:        +45.0°C  (high = +80.0°C, crit = +100.0°C)

nct6775-isa-0290
Adapter: ISA adapter
fan1:        1200 RPM
fan2:        1500 RPM
temp1:       +30.0°C  (high = +60.0°C, crit = +90.0°C)
temp2:       +35.0°C  (high = +60.0°C, crit = +90.0°C)
Vcore:       +1.200 V  (min = +0.850 V, max = +1.400 V)
```

## 2\. Other Useful Tools and Front-ends

While `lm_sensors` provides the raw data, many other tools can present this information in a more user-friendly or advanced way.

  * **`hddtemp` (for Hard Drive Temperature):**

      * **Installation:** `sudo apt install hddtemp` (Debian/Ubuntu) or equivalent for your distro.
      * **Usage:** `sudo hddtemp /dev/sda` (replace `/dev/sda` with your hard drive device).
      * *Note: Many modern drives use SMART data, which can also be read by tools like `smartctl`.*

  * **`psensor` (Graphical Front-end):**
    `psensor` is a popular GTK+ application that provides a graphical interface for `lm_sensors`, `hddtemp`, and even some Nvidia GPU temperatures. It can display graphs, set alerts, and show system tray icons.

      * **Installation:** `sudo apt install psensor`
      * **Usage:** Launch `psensor` from your applications menu.

  * **`glances` (Comprehensive System Monitor):**
    `glances` is a cross-platform command-line tool that offers a real-time overview of your system, including CPU, memory, disk I/O, network, and also sensor data (using `lm_sensors` and `hddtemp`).

      * **Installation:** `sudo apt install glances`
      * **Usage:** `glances` then press `f` to toggle sensor information.

  * **`netdata` (Web-based System Monitor):**
    `netdata` is a highly detailed, real-time performance monitoring system that runs as a web server on your Linux machine. It collects a vast array of metrics, including sensor data, and presents them through an interactive web interface.

      * **Installation:** Follow the instructions on the Netdata GitHub page, as it's typically installed via a one-line script.
      * **Usage:** Access it via your web browser at `http://localhost:19999` (or the server's IP).

  * **`btop` (Modern Command-line Monitor):**
    `btop` is a feature-rich and visually appealing command-line system monitor that often integrates sensor data alongside other system metrics like CPU, memory, disk, and network.

      * **Installation:** Often available in package managers (`sudo apt install btop`).
      * **Usage:** `btop`

  * **Prometheus & Grafana:**
    For more advanced and long-term monitoring, especially in server environments, Prometheus is a powerful time-series database that can scrape metrics (including sensor data via a "node exporter") and Grafana is used for creating highly customizable dashboards to visualize that data. This is a more involved setup for comprehensive monitoring.

**Key Concepts:**

  * **Kernel Modules:** These are small programs that extend the functionality of the Linux kernel. Sensor monitoring relies on specific kernel modules to interface with the hardware chips.
  * **`sysfs`:** Linux exposes a lot of hardware and kernel information through the `sysfs` filesystem, which is often where tools like `lm_sensors` retrieve their data.
  * **Super I/O Chips:** These are integrated circuits on motherboards that handle various low-speed functions, including temperature and fan control. `lm_sensors` often interacts with these chips.

By using `lm_sensors` and its various front-ends, you can effectively monitor the health and performance of your Linux system's hardware.