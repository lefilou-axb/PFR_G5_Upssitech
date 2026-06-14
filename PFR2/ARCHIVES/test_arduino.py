import serial
import time

ser = serial.Serial('COM3', 115200, timeout=1)

print("="*50)
print("Monitoring Arduino sur COM3...")
print("Appuyer Ctrl+C pour arrêter")
print("="*50 + "\n")

try:
    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').strip()
            print(f"[Arduino] {data}")
            
except KeyboardInterrupt:
    print("\n✓ Déconnecté")
    ser.close()