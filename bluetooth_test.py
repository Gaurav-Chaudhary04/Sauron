import serial
import time

BLUETOOTH_PORT = "COM8"  # Update this with your actual port
BAUD_RATE = 9600
QUEUE_FILE = "queue_data.txt"
BATCH_DURATION = 7  # Seconds
SAMPLE_INTERVAL = 1  # Read data every second
THRESHOLD_PERCENTAGE = 70  # 70% threshold

def read_bluetooth():
    try:
        bt_serial = serial.Serial(BLUETOOTH_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Allow Bluetooth to stabilize
        print("✅ Connected to Bluetooth. Waiting for data...\n")

        while True:
            sensor1_data = []
            sensor2_data = []

            # Collect values for 7 seconds
            for _ in range(BATCH_DURATION):
                data = bt_serial.readline().decode().strip()
                if data:
                    print(f"📡 Received: {data}")

                    if "Sensor1:" in data and "Sensor2:" in data:
                        parts = data.split(", ")
                        sensor1_status = int(parts[0].split(":")[-1].strip())  
                        sensor2_status = int(parts[1].split(":")[-1].strip())  

                        sensor1_data.append(sensor1_status)
                        sensor2_data.append(sensor2_status)

                time.sleep(SAMPLE_INTERVAL)

            # Compute percentage of `1` values
            sensor1_percentage = (sum(sensor1_data) / len(sensor1_data)) * 100
            sensor2_percentage = (sum(sensor2_data) / len(sensor2_data)) * 100

            # Decide final queue value
            sensor1_final = 1 if sensor1_percentage >= THRESHOLD_PERCENTAGE else 0
            sensor2_final = 1 if sensor2_percentage >= THRESHOLD_PERCENTAGE else 0

            print(f"📊 Sensor 1 Final Decision: {sensor1_final} (Based on {sensor1_percentage:.2f}% 1s)")
            print(f"📊 Sensor 2 Final Decision: {sensor2_final} (Based on {sensor2_percentage:.2f}% 1s)")

            # Convert to queue length
            if sensor1_final == 0 and sensor2_final == 0:
                queue_length = 0
            elif sensor1_final == 1 and sensor2_final == 0:
                queue_length = 200
            elif sensor1_final == 0 and sensor2_final == 1:
                queue_length = 0
            else:  # sensor1_final == 1 and sensor2_final == 1
                queue_length = 400

            print(f"🚦 Updated Queue Length: {queue_length}m")

            # Save to file
            with open(QUEUE_FILE, "w") as f:
                f.write(str(queue_length))

    except serial.SerialException:
        print("❌ Bluetooth Error: Check connection.")
    except Exception as e:
        print(f"⚠️ Error: {e}")
    finally:
        if 'bt_serial' in locals():
            bt_serial.close()
            print("🔌 Bluetooth disconnected.")

if __name__ == "__main__":
    read_bluetooth()
