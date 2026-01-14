import csv
import numpy as np
import time
import ADS1256
import RPi.GPIO as GPIO

def AD8302_voltage_to_dB(voltage):
    return voltage * 34.87 -31.58

def AD8302_volt_to_degree(volt):
  return volt * 100 - 180.08
  
def complex_convert(real, imag):
    return real + 1j * imag

def desibell(real, imag):
    return 20 * np.log10((np.sqrt(real**2 + imag**2)) + 1e-3)


def osl_calibration(measured_short, measured_open, measured_load, measured_DUT):
    """
    Basitleştirilmiş OSL kalibrasyonu.

    Args:
        measured_open: Açık standardının ölçülen S-parametreleri (karmaşık sayı).
        measured_short: Kısa standardının ölçülen S-parametreleri (karmaşık sayı).
        measured_load: Yük standardının ölçülen S-parametreleri (karmaşık sayı).
        measured_DUT: Ölçülen cihazın (DUT) S-parametreleri (karmaşık sayı).

    Returns:
        Düzeltilmiş DUT S-parametreleri (karmaşık sayı).
    """

    e00 = measured_load
    e11 = (-2 * e00 + measured_short + measured_open) / (-measured_short + measured_open + 1e-12)
    e01e10 = (measured_open - e00) * (1 - e11)


    #gamma_dut_c = (measured_DUT - e00) / (1 - e11 * measured_DUT) / e01e10
    gamma_dut_c = (measured_DUT - e00) / (e01e10 + e11 * (measured_DUT - e00) + 1e-12)
    return gamma_dut_c

def magnitude_phase_to_real_imag(voltage, phase_deg):
    phase_rad = np.radians(phase_deg)  # Dereceyi radyana çevir
    real = voltage * np.cos(phase_rad)
    imag = voltage * np.sin(phase_rad)
    return real, imag


class DataAcquisition:
    def __init__(self):
        self.intervals = 0.001
        self.csv_file_path = "/home/pi/Desktop/kontrol.csv"
        
        # Set up CSV file
        self.csv_file = open(self.csv_file_path, mode='w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(['Zaman (s)', '1.Gerilim (V)', '2.Gerilim (V)'])
        # Acquisition control
        self.acquisition_active = True
        self.start_time = time.perf_counter()
        
    def start_acquisition(self):  
        try:
            ADC = ADS1256.ADS1256()
            ADC.ADS1256_init()  
            new_value = [0,0]
            
             
            #time.sleep(2)#stabilizasyon için gerekli
            while self.acquisition_active:
                current_time = time.perf_counter() - self.start_time
                
                ADC_Value = ADC.ADS1256_GetAll()
                    
                # Generate square wave value based on sine wave sign
                new_value[0]= ADC_Value[0]*5.0/0x7fffff
                new_value[1]= ADC_Value[1]*5.0/0x7fffff
                
                
                # Save to CSV immediately for each sample to ensure all data is captured
                self.csv_writer.writerow([current_time, new_value[0], new_value[1]])
                
                # Target the next sample time precisely at 1 ms intervals
                target_time = self.start_time + (current_time + self.intervals)
                while time.perf_counter() <= target_time:
                    pass  # Busy-wait until the exact 1 ms interval

        except KeyboardInterrupt:
            self.stop_acquisition()
            GPIO.cleanup()
            print("Data acquisition stopped.")
            exit()
            
    def stop_acquisition(self):
        self.acquisition_active = False
        self.csv_file.close()

if __name__ == "__main__":
    acquisition = DataAcquisition()
    print("Data acquisition started. Press Ctrl+C to stop.")
    acquisition.start_acquisition()
