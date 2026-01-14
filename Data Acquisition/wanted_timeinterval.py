import csv
import numpy as np
import time
import matplotlib.pyplot as plt
from threading import Thread
import ADS1256
import RPi.GPIO as GPIO

class DataAcquisition:
    def __init__(self):
        self.csv_file_path = "/home/pi/Desktop/veeeee.csv"
        self.intervals = 0.001
        self.acquisition_active = True
        self.start_time = time.perf_counter()

        # CSV Dosyasını hazırla
        self.csv_file = open(self.csv_file_path, mode='w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(['Zaman (s)', 'Gerilim (V)'])

    def start_acquisition(self):
        try:
            while self.acquisition_active:
                current_time = time.perf_counter() - self.start_time
                
                ADC_Value = ADC.ADS1256_GetAll()

                new_value = ADC_Value[0]*5.0/0x7fffff
                
                self.csv_writer.writerow([current_time, new_value])
                
                target_time = self.start_time + current_time + self.intervals
                while time.perf_counter() <= target_time:
                    pass  # Busy-wait until the exact 1 ms interval

        except KeyboardInterrupt:
            self.stop_acquisition()
            print("Veri toplama durduruldu.")
            GPIO.cleanup()
            print ("\r\nProgram end     ")
            exit()

    def stop_acquisition(self):
        self.acquisition_active = False
        self.csv_file.close()

    def plot_from_csv(self, start_time, end_time):
        try:
            times, values = [], []
            with open(self.csv_file_path, mode='r') as file:
                reader = csv.reader(file)
                next(reader)  # Başlık satırını atla
                for row in reader:
                    time_val, value = float(row[0]), float(row[1])
                    if start_time <= time_val <= end_time:
                        times.append(time_val)
                        values.append(value)

            plt.figure()
            plt.plot(times, values, label=f"{start_time}s - {end_time}s")
            plt.xlabel("Zaman (s)")
            plt.ylabel("Gerilim (V)")
            plt.title("Seçilen Zaman Aralığı")
            plt.legend()
            plt.grid()
            plt.show()
        except Exception as e:
            print(f"Hata: {e}")

if __name__ == "__main__":
    ADC = ADS1256.ADS1256()
    ADC.ADS1256_init()

    acquisition = DataAcquisition()

    # Veri toplama işlemini başlat
    acquisition_thread = Thread(target=acquisition.start_acquisition)
    acquisition_thread.start()

    # Grafik çizim komutlarını isteğe bağlı tetikleyin
    while True:
        try:
            start_time = float(input("Başlangıç zamanını girin (s): "))
            end_time = float(input("Bitiş zamanını girin (s): "))
            acquisition.plot_from_csv(start_time, end_time)
        except KeyboardInterrupt:
            acquisition.stop_acquisition()
            print("Program durduruldu.")
            break
