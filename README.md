# High-Precision Data Acquisition System

A Python-based data acquisition system designed for the Raspberry Pi, utilizing the Waveshare ADS1256 High-Precision AD/DA Board. This system captures analog signals, performs real-time sampling rate monitoring, logs data, and provides visualization tools.

## Features

- **High-Precision ADC**: Drivers and interface for the ADS1256 24-bit ADC module.
- **Real-Time Monitoring**: Live calculation and display of Samples Per Second (SPS).
- **Data Logging**: Captures dual-channel voltage data and saves it to CSV format with precise timing.
- **Interactive Visualization**: Run data acquisition in the background while plotting specific time intervals on demand (`wanted_timeinterval.py`).
- **Real-Time Graphing**: Live plotting of calibrated sensor data (`periodic_graphic.py`).
- **Signal Processing**: 
  - AD8302 Gain/Phase detector conversion.
  - Complex number manipulation.
  - OSL (Open-Short-Load) calibration implementation for RF measurements.

## Hardware Requirements

- **Raspberry Pi** (3B, 4B, or compatible)
- **Waveshare ADS1256 High-Precision AD/DA Board**
- Sensors or signal sources for input

## Pin Configuration

The system uses the standard SPI interface on the Raspberry Pi.

| ADS1256 | Raspberry Pi (BCM) | Physical Pin |
|---------|-------------------|--------------|
| 5V      | 5V                | 2, 4         |
| GND     | GND               | 6, 9, etc.   |
| DIN     | MOSI (GPIO 10)    | 19           |
| DOUT    | MISO (GPIO 9)     | 21           |
| SCLK    | SCLK (GPIO 11)    | 23           |
| CS      | GPIO 22           | 15           |
| DRDY    | GPIO 17           | 11           |
| RST     | GPIO 18           | 12           |

*Note: Pin mappings can be modified in `config.py`.*

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/hbk-0/data-acquisition.git
    cd data-acquisition
    ```

2.  **Install Dependencies:**
    Ensure you have Python 3 installed. You will need logic for GPIO, SPI, and plotting:
    ```bash
    sudo apt-get update
    sudo apt-get install python3-pip python3-numpy python3-matplotlib
    sudo pip3 install RPi.GPIO spidev
    ```

3.  **Enable SPI:**
    Make sure the SPI interface is enabled on your Raspberry Pi:
    ```bash
    sudo raspi-config
    # Navigate to Interfacing Options -> SPI -> Yes
    ```

## Usage

### 1. Simple Monitoring Demo
To verify the hardware connection and check the sampling rate:
```bash
sudo python3 main.py
```

### 2. Standard Data Logging
To log data to a CSV file with OSL calibration logic:
```bash
python3 data_acquisition.py
```

### 3. Interactive Logging & Plotting
To log data in the background and interactively plot specific time intervals without stopping the acquisition:
```bash
python3 wanted_timeinterval.py
```
*Follow the on-screen prompts to enter start and end times (in seconds) to visualize that segment.*

### 4. Real-Time Calibrated Graphing
To view a live graph of the calibrated data:
```bash
python3 periodic_graphic.py
```

## Project Structure

- **`main.py`**: Entry point for testing and real-time SPS monitoring.
- **`data_acquisition.py`**: Core logic for logging data, calibration, and signal processing.
- **`wanted_timeinterval.py`**: Threaded data acquisition with on-demand plotting of historical buffered data.
- **`periodic_graphic.py`**: Real-time graphing tool with OSL calibration applied.
- **`ADS1256.py`**: Driver class for the ADS1256 hardware.
- **`config.py`**: Hardware abstraction layer (HAL) handling GPIO and SPI communications.
- **`readme.txt`**: Original hardware documentation and pinout reference.

## Contributing

Contributions, issues, and feature requests are welcome!

## License

[MIT](LICENSE)
