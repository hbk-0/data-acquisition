import csv
import numpy as np
import time
import matplotlib.pyplot as plt
import ADS1256
import RPi.GPIO as GPIO

pattern = r"VMAG:\s*([\d\.]+)\s*V,\s*VPHASE:\s*([\d\.]+)\s*V"

def AD8302_voltage_to_dB(voltage):
    return (voltage - 0.9) / 0.03

def AD8302_volt_to_degree(volt):
  return (volt - 0.9) / 0.01

def complex_convert(real, imag):
    return real * np.exp(2 * np.pi * 1j * imag)

def desibell(real, imag):
    return 20 * np.log10((np.sqrt(real*2 + imag*2)) + 1e-3)

def magnitude_phase_to_real_imag(voltage, phase_deg):
    phase_rad = phase_deg * np.pi / 180
    return voltage * np.cos(phase_rad), voltage * np.sin(phase_rad)

def osl_calibration_vmag_vphase(short_value, open_value, load_value, measured_value):
    """
    Open-Short-Load (OSL) kalibrasyonu ile sensör verisini düzelten fonksiyon.

    Parametreler:
    measured_value : Ölçülen ham sensör değeri
    open_value : Open yükü bağlandığında ölçülen değer
    short_value : Short yükü bağlandığında ölçülen değer
    load_value : Load yükü bağlandığında ölçülen değer
    sensor_value : Kalibre edilecek sensör değeri

    Dönüş:
    Kalibre edilmiş sensör değeri
    """
    # Beklenen değerler
    expected_open = 0.9
    expected_short = 0.9
    expected_load = 1.8

    # Hata terimlerini hesapla
    e00 = open_value - expected_open  # Directivity error
    e01 = (short_value - expected_short - e00) / (-1)  # Source match error (S_short ideal -1)
    e10 = (load_value - expected_load - e00) / (1 - e01 * 0)  # Reflection tracking error (S_load ideal 0)

    # Sensör değerini kalibre et
    calibrated_value = (measured_value - e00) / (1 - e01 * measured_value)

    return calibrated_value

def osl_phase(short_value, open_value, load_value, measured_value):
    """
    Open-Short-Load (OSL) kalibrasyonu ile faz verisini düzelten fonksiyon.

    Parametreler:
    measured_phase : Ölçülen ham faz değeri
    open_phase : Open yükü bağlandığında ölçülen faz değeri
    short_phase : Short yükü bağlandığında ölçülen faz değeri
    load_phase : Load yükü bağlandığında ölçülen faz değeri
    sensor_phase : Kalibre edilecek sensör faz değeri

    Dönüş:
    Kalibre edilmiş faz değeri
    """
    # Beklenen faz değerleri (voltaj olarak değil, derece olarak hesaplanıyor)
    expected_open_phase = 90  # Open için ideal faz
    expected_short_phase = -90  # Short için ideal faz
    expected_load_phase = 0  # Load için ideal faz

    # Hata terimlerini hesapla
    e00_phase = open_value - expected_open_phase  # Directivity error
    e01_phase = (short_value - expected_short_phase - e00_phase) / (-1)  # Source match error
    e10_phase = (load_value - expected_load_phase - e00_phase) / (1 - e01_phase * 0)  # Reflection tracking error

    # Sensör faz değerini kalibre et
    calibrated_phase = (measured_value - e00_phase) / (1 - e01_phase * measured_value)

    return calibrated_phase



def calibration(sensor_mag, sensor_phase, load_mag, load_phase, open_mag, open_phase, short_mag, short_phase):

    calibrated_sensor_mag_voltage = osl_calibration_vmag_vphase(
        short_mag,
        open_mag,
        load_mag,
        sensor_mag
    )
    calibrated_sensor_mag_voltage_updated= AD8302_voltage_to_dB(calibrated_sensor_mag_voltage)
    
    calibrated_sensor_phase_voltage = osl_phase(
        AD8302_volt_to_degree(short_phase),
        AD8302_volt_to_degree(open_phase),
        AD8302_volt_to_degree(load_phase),
        AD8302_volt_to_degree(sensor_phase)
    )

    mag = 10**(calibrated_sensor_mag_voltage_updated/20)
    real, imag = magnitude_phase_to_real_imag(mag, calibrated_sensor_phase_voltage)
    sensor_1000 = -desibell(real, imag)

    return sensor_1000





class DataAcquisition:
        
        
    def __init__(self):
        self.counter = 0
        self.size_of_graph = 100
        plt.ion()
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], lw=2)
        self.ax.set_ylim(-35,0)  # Sensör voltaj aralığı 0-1.1V

        self.intervals = 0.1

        self.x_data = []
        self.y_data = []

        self.csv_file_path = "/home/pi/Desktop/periodic.csv"
        # Set up CSV file
        self.csv_file = open(self.csv_file_path, mode='w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(['Zaman (s)', 'Gerilim (V)'])
        
        # Acquisition control
        self.acquisition_active = True
        self.start_time = time.perf_counter()

    def update_graph(self):
        self.ax.clear()
        self.ax.plot(self.x_data, self.y_data)
        self.ax.set_xlabel("Zaman (s)")
        self.ax.set_ylabel("Gerilim (V)")
        plt.draw()
        plt.pause(0.01)

    def start_acquisition(self):
        try:
            ADC = ADS1256.ADS1256() 
            ADC.ADS1256_init()
            new_value = [0,0]
            while self.acquisition_active:
                current_time = time.perf_counter() - self.start_time
                
                ADC_Value = ADC.ADS1256_GetAll()
                new_value[0] = ADC_Value[0]*5.0/0x7fffff
                new_value[1] = ADC_Value[1]*5.0/0x7fffff
                
                short_mag = 0.78
                short_phase = 0.784
                
                open_mag = 0.932
                open_phase = 1.272
                
                load_mag = 1.043
                load_phase = 1.747
                
                sensor_dB = calibration(new_value[0], new_value[1], load_mag, load_phase, open_mag, open_phase, short_mag, short_phase)
                
                self.x_data.append(current_time)
                self.y_data.append(sensor_dB)
                self.csv_writer.writerow([current_time, sensor_dB])
                
                self.counter += 1 
                if self.counter % self.size_of_graph == 0:
                    self.update_graph()
                    self.x_data.clear()
                    self.y_data.clear()

                # Target the next sample time precisely at 1 ms intervals
                target_time = self.start_time + current_time + self.intervals
                while time.perf_counter() <= target_time:
                    pass  # Busy-wait until the exact 1 ms interval

        except KeyboardInterrupt:
            self.stop_acquisition()
            print("Data acquisition stopped.")
            GPIO.cleanup()
            exit()

    def stop_acquisition(self):
        self.acquisition_active = False
        self.csv_file.close()

if __name__ == "__main__":
    acquisition = DataAcquisition()
    print("Data acquisition started. Press Ctrl+C to stop.")
    acquisition.start_acquisition()       



