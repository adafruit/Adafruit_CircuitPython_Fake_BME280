# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""
Example showing how the BME280 library can be used to set the various
parameters supported by the sensor.
Refer to the BME280 datasheet to understand what these parameters do

NOTE: This is a mock. The settings exposed here are simply stored and read back.
"""

import time
import board
from fake_bme280 import advanced as adafruit_bme280

# Create sensor object, using the board's default I2C bus.
i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
# Return random plausible readings with no network access or configuration.
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, use_openweather=False)
# OR fetch live data from the OpenWeatherMap API (requires settings.toml/.env)
# bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, use_openweather=True)

# Configure the sensor with non-default settings and store in the `bme280` object
bme280.sea_level_pressure = 1013.25
bme280.mode = adafruit_bme280.MODE_NORMAL
bme280.standby_period = adafruit_bme280.STANDBY_TC_500
bme280.iir_filter = adafruit_bme280.IIR_FILTER_X16
bme280.overscan_pressure = adafruit_bme280.OVERSCAN_X16
bme280.overscan_humidity = adafruit_bme280.OVERSCAN_X1
bme280.overscan_temperature = adafruit_bme280.OVERSCAN_X2

# Print out the settings to confirm storage in the `bme280` object
print(f"Mode: {bme280.mode}")
print(f"Standby Period: {bme280.standby_period}")
print(f"IIR Filter: {bme280.iir_filter}")
print(f"Overscan Pressure: {bme280.overscan_pressure}")
print(f"Overscan Humidity: {bme280.overscan_humidity}")
print(f"Overscan Temperature: {bme280.overscan_temperature}")

# The sensor will need a moment to gather initial readings
time.sleep(1)

while True:
    print(f"\nTemperature: {bme280.temperature:0.1f} C")
    print(f"Humidity: {bme280.relative_humidity:0.1f} %")
    print(f"Pressure: {bme280.pressure:0.1f} hPa")
    print(f"Altitude = {bme280.altitude:0.2f} meters")
    time.sleep(2)
