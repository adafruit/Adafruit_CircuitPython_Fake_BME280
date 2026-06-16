# SPDX-FileCopyrightText: 2017 ladyada for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`fake_bme280.advanced`
=========================================================================================

CircuitPython driver from BME280 Temperature, Humidity and Barometric
Pressure sensor

NOTE: This is a mock. The settings exposed here are simply stored and read back.

* Author(s): ladyada, Jose David M.

Implementation Notes
--------------------

**Hardware:**

* `Adafruit BME280 Temperature, Humidity and Barometric Pressure sensor
  <https://www.adafruit.com/product/2652>`_ (Product ID: 2652)


**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads
"""

from micropython import const

from fake_bme280.basic import Adafruit_BME280
from fake_bme280.protocol import I2C_Impl

try:
    import typing  # pylint: disable=unused-import

    from busio import I2C
except ImportError:
    pass

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/brentru/CircuitPython_Fake_BME280.git"

#    I2C ADDRESS/BITS/SETTINGS
#    -----------------------------------------------------------------------
_BME280_ADDRESS = const(0x77)

"""iir_filter values"""
IIR_FILTER_DISABLE = const(0)
IIR_FILTER_X2 = const(0x01)
IIR_FILTER_X4 = const(0x02)
IIR_FILTER_X8 = const(0x03)
IIR_FILTER_X16 = const(0x04)

_BME280_IIR_FILTERS = (
    IIR_FILTER_DISABLE,
    IIR_FILTER_X2,
    IIR_FILTER_X4,
    IIR_FILTER_X8,
    IIR_FILTER_X16,
)

"""overscan values for temperature, pressure, and humidity"""
OVERSCAN_DISABLE = const(0x00)
OVERSCAN_X1 = const(0x01)
OVERSCAN_X2 = const(0x02)
OVERSCAN_X4 = const(0x03)
OVERSCAN_X8 = const(0x04)
OVERSCAN_X16 = const(0x05)

_BME280_OVERSCANS = {
    OVERSCAN_DISABLE: 0,
    OVERSCAN_X1: 1,
    OVERSCAN_X2: 2,
    OVERSCAN_X4: 4,
    OVERSCAN_X8: 8,
    OVERSCAN_X16: 16,
}

"""mode values"""
MODE_SLEEP = const(0x00)
MODE_FORCE = const(0x01)
MODE_NORMAL = const(0x03)

_BME280_MODES = (MODE_SLEEP, MODE_FORCE, MODE_NORMAL)
"""
standby timeconstant values
TC_X[_Y] where X=milliseconds and Y=tenths of a millisecond
"""
STANDBY_TC_0_5 = const(0x00)  # 0.5ms
STANDBY_TC_10 = const(0x06)  # 10ms
STANDBY_TC_20 = const(0x07)  # 20ms
STANDBY_TC_62_5 = const(0x01)  # 62.5ms
STANDBY_TC_125 = const(0x02)  # 125ms
STANDBY_TC_250 = const(0x03)  # 250ms
STANDBY_TC_500 = const(0x04)  # 500ms
STANDBY_TC_1000 = const(0x05)  # 1000ms

_BME280_STANDBY_TCS = (
    STANDBY_TC_0_5,
    STANDBY_TC_10,
    STANDBY_TC_20,
    STANDBY_TC_62_5,
    STANDBY_TC_125,
    STANDBY_TC_250,
    STANDBY_TC_500,
    STANDBY_TC_1000,
)


class Adafruit_BME280_Advanced(Adafruit_BME280):
    """Driver from BME280 Temperature, Humidity and Barometric Pressure sensor

    .. note::
        This is a mock. The settings exposed here are simply stored and read
        back - nothing is written to a real device.

    """

    @property
    def standby_period(self) -> int:
        """
        Control the inactive period when in Normal mode
        Allowed standby periods are the constants STANDBY_TC_*
        """
        return self._t_standby

    @standby_period.setter
    def standby_period(self, value: int) -> None:
        if not value in _BME280_STANDBY_TCS:
            raise ValueError(f"Standby Period '{value}' not supported")
        self._t_standby = value

    @property
    def overscan_humidity(self) -> int:
        """
        Humidity Oversampling
        Allowed values are the constants OVERSCAN_*
        """
        return self._overscan_humidity

    @overscan_humidity.setter
    def overscan_humidity(self, value: int) -> None:
        if not value in _BME280_OVERSCANS:
            raise ValueError(f"Overscan value '{value}' not supported")
        self._overscan_humidity = value

    @property
    def overscan_temperature(self) -> int:
        """
        Temperature Oversampling
        Allowed values are the constants OVERSCAN_*
        """
        return self._overscan_temperature

    @overscan_temperature.setter
    def overscan_temperature(self, value: int) -> None:
        if not value in _BME280_OVERSCANS:
            raise ValueError(f"Overscan value '{value}' not supported")
        self._overscan_temperature = value

    @property
    def overscan_pressure(self) -> int:
        """
        Pressure Oversampling
        Allowed values are the constants OVERSCAN_*
        """
        return self._overscan_pressure

    @overscan_pressure.setter
    def overscan_pressure(self, value: int) -> None:
        if not value in _BME280_OVERSCANS:
            raise ValueError(f"Overscan value '{value}' not supported")
        self._overscan_pressure = value

    @property
    def iir_filter(self) -> int:
        """
        Controls the time constant of the IIR filter
        Allowed values are the constants IIR_FILTER_*
        """
        return self._iir_filter

    @iir_filter.setter
    def iir_filter(self, value: int) -> None:
        if not value in _BME280_IIR_FILTERS:
            raise ValueError(f"IIR Filter '{value}' not supported")
        self._iir_filter = value

    @property
    def measurement_time_typical(self) -> float:
        """Typical time in milliseconds required to complete a measurement in normal mode"""
        meas_time_ms = 1.0
        if self.overscan_temperature != OVERSCAN_DISABLE:
            meas_time_ms += 2 * _BME280_OVERSCANS.get(self.overscan_temperature)
        if self.overscan_pressure != OVERSCAN_DISABLE:
            meas_time_ms += 2 * _BME280_OVERSCANS.get(self.overscan_pressure) + 0.5
        if self.overscan_humidity != OVERSCAN_DISABLE:
            meas_time_ms += 2 * _BME280_OVERSCANS.get(self.overscan_humidity) + 0.5
        return meas_time_ms

    @property
    def measurement_time_max(self) -> float:
        """Maximum time in milliseconds required to complete a measurement in normal mode"""
        meas_time_ms = 1.25
        if self.overscan_temperature != OVERSCAN_DISABLE:
            meas_time_ms += 2.3 * _BME280_OVERSCANS.get(self.overscan_temperature)
        if self.overscan_pressure != OVERSCAN_DISABLE:
            meas_time_ms += 2.3 * _BME280_OVERSCANS.get(self.overscan_pressure) + 0.575
        if self.overscan_humidity != OVERSCAN_DISABLE:
            meas_time_ms += 2.3 * _BME280_OVERSCANS.get(self.overscan_humidity) + 0.575
        return meas_time_ms


class Adafruit_BME280_I2C(Adafruit_BME280_Advanced):
    """Driver for BME280 connected over I2C

    :param ~busio.I2C i2c: The I2C bus the BME280 is connected to.
    :param int address: I2C device address. Defaults to :const:`0x77`.
                        but another address can be passed in as an argument

    .. note::
        The operational range of the BMP280 is 300-1100 hPa.
        Pressure measurements outside this range may not be as accurate.

    **Quickstart: Importing and using the BME280**

    Here is an example of using the :class:`Adafruit_BME280_I2C`.
    First you will need to import the libraries to use the sensor

    .. code-block:: python

        import board
        import fake_bme280.advanced as adafruit_bme280

    Once this is done you can define your `board.I2C` object and define your sensor object

    .. code-block:: python

        i2c = board.I2C()   # uses board.SCL and board.SDA
        bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

    You need to setup the pressure at sea level

    .. code-block:: python

        bme280.sea_level_pressure = 1013.25

    Now you have access to the :attr:`temperature`, :attr:`relative_humidity`
    :attr:`pressure` and :attr:`altitude` attributes

    .. code-block:: python

        temperature = bme280.temperature
        relative_humidity = bme280.relative_humidity
        pressure = bme280.pressure
        altitude = bme280.altitude

    """

    def __init__(
        self,
        i2c: I2C,
        address: int = _BME280_ADDRESS,
        use_openweather: bool = True,
    ) -> None:
        super().__init__(I2C_Impl(i2c, address), use_openweather=use_openweather)
