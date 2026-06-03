# SPDX-FileCopyrightText: 2017 ladyada for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`fake_bme280.basic`
=========================================================================================

CircuitPython driver from BME280 Temperature, Humidity and Barometric
Pressure sensor

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

import math
import os
import random
import socket as pool
import ssl
import typing  # pylint: disable=unused-import
from micropython import const
import adafruit_requests
from fake_bme280.protocol import I2C_Impl, SPI_Impl

try:
    import toml
except ImportError:
    toml = None

try:
    import dotenv
except ImportError:
    dotenv = None

try:
    from busio import I2C, SPI
    from digitalio import DigitalInOut
except ImportError:
    pass

__version__ = "2.6.4"
__repo__ = "https://github.com/brentru/CircuitPython_Fake_BME280.git"

#    I2C ADDRESS/BITS/SETTINGS
#    -----------------------------------------------------------------------

"""General Information"""
_BME280_ADDRESS = const(0x77)
_BME280_CHIPID = const(0x60)
_BME280_REGISTER_CHIPID = const(0xD0)
"""overscan values for temperature, pressure, and humidity"""
OVERSCAN_X1 = const(0x01)
OVERSCAN_X16 = const(0x05)
"""mode values"""
_BME280_MODES = (0x00, 0x01, 0x03)
"""iir_filter values"""
IIR_FILTER_DISABLE = const(0)
"""
standby timeconstant values
TC_X[_Y] where X=milliseconds and Y=tenths of a millisecond
"""
STANDBY_TC_125 = const(0x02)  # 125ms
"""mode values"""
MODE_SLEEP = const(0x00)
MODE_FORCE = const(0x01)
MODE_NORMAL = const(0x03)
"""Other Registers"""
_BME280_REGISTER_SOFTRESET = const(0xE0)
_BME280_REGISTER_CTRL_HUM = const(0xF2)
_BME280_REGISTER_STATUS = const(0xF3)
_BME280_REGISTER_CTRL_MEAS = const(0xF4)
_BME280_REGISTER_CONFIG = const(0xF5)
_BME280_REGISTER_TEMPDATA = const(0xFA)
_BME280_REGISTER_HUMIDDATA = const(0xFD)

_OPENWEATHER_KEYS = (
    "openweather_location",
    "openweather_units",
    "openweather_token",
)

_SETTINGS_TOML_PATH = "settings.toml"


def _load_openweather_settings() -> dict:
    """Return OpenWeatherMap settings, trying settings.toml, then .env
    (python-dotenv), then os.getenv, per key in that order. Raises
    ``RuntimeError`` if settings.toml is malformed or any key is missing."""
    toml_values = {}
    if toml is not None:
        try:
            toml_values = toml.load(_SETTINGS_TOML_PATH)
        except FileNotFoundError:
            pass
        except toml.TomlDecodeError as err:
            raise RuntimeError(
                "Could not parse %s: %s" % (_SETTINGS_TOML_PATH, err)
            ) from err

    dotenv_values = dotenv.dotenv_values() if dotenv is not None else {}

    settings = {}
    for key in _OPENWEATHER_KEYS:
        value = toml_values.get(key) or dotenv_values.get(key) or os.getenv(key)
        if value:
            settings[key] = value

    missing = [k for k in _OPENWEATHER_KEYS if k not in settings]
    if missing:
        raise RuntimeError(
            "fake_bme280 is missing required OpenWeatherMap setting(s): "
            + ", ".join(missing)
            + ". Provide them via settings.toml, a .env file (python-dotenv), "
            "or environment variables. Or construct the sensor with "
            "use_openweather=False for random fake readings (no network)."
        )
    return settings


def _build_openweather_url() -> str:
    """Build the OpenWeatherMap API URL from the loaded settings."""
    config = _load_openweather_settings()
    return (
        "http://api.openweathermap.org/data/2.5/weather?q="
        + config["openweather_location"]
        + "&units="
        + config["openweather_units"]
        + "&mode=json&appid="
        + config["openweather_token"]
    )


class Adafruit_BME280:
    """Driver from BME280 Temperature, Humidity and Barometric Pressure sensor

    .. note::
        The operational range of the BME280 is 300-1100 hPa.
        Pressure measurements outside this range may not be as accurate.

    """

    # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        bus_implementation: typing.Union[I2C_Impl, SPI_Impl],
        use_openweather: bool = True,
    ) -> None:
        """Mock a BME280 sensor object that was found on an I2C bus.

        :param bus_implementation: I2C or SPI implementation wrapper.
        :param bool use_openweather: When ``True`` (default), read settings
            from the environment (``settings.toml`` on CircuitPython,
            environment variables on CPython) and fetch live data from the
            OpenWeatherMap API. When ``False``, return random plausible
            readings with no network access and no configuration required.
        """
        self._bus_implementation = bus_implementation
        self._iir_filter = IIR_FILTER_DISABLE
        self.overscan_humidity = OVERSCAN_X1
        self.overscan_temperature = OVERSCAN_X1
        self.overscan_pressure = OVERSCAN_X16
        self._t_standby = STANDBY_TC_125
        self._mode = MODE_SLEEP
        self.sea_level_pressure = 1013.25
        """Pressure in hectoPascals at sea level. Used to calibrate `altitude`."""
        self._t_fine = None
        self._use_openweather = use_openweather
        self._current_forecast = None
        self._data_source = None
        self.requests = None
        if use_openweather:
            self._data_source = _build_openweather_url()
            self.requests = adafruit_requests.Session(
                pool, ssl.create_default_context()
            )
            self.get_forecast()
        else:
            self._current_forecast = self._random_forecast()

    @staticmethod
    def _random_forecast() -> dict:
        """Generate a plausible BME280-shaped reading."""
        return {
            "main": {
                "temp": round(random.uniform(18.0, 28.0), 2),
                "pressure": round(random.uniform(1000.0, 1025.0), 2),
                "humidity": round(random.uniform(30.0, 70.0), 2),
            }
        }

    def get_forecast(self):
        """Fetch weather from OpenWeatherMap (or generate fake data)."""
        if not self._use_openweather:
            self._current_forecast = self._random_forecast()
            return
        response = self.requests.get(self._data_source)
        self._current_forecast = response.json()

    def _read_temperature(self) -> None:
        # Get the OpenWeather temperature and store it in _t_fine
        self.get_forecast()
        self._t_fine = self._current_forecast["main"]["temp"]

    @property
    def mode(self) -> int:
        """
        Operation mode
        Allowed values are the constants MODE_*
        """
        return self._mode

    @mode.setter
    def mode(self, value: int) -> None:
        if not value in _BME280_MODES:
            raise ValueError("Mode '%s' not supported" % (value))
        self._mode = value

    @property
    def _config(self) -> int:
        """Value to be written to the device's config register"""
        config = 0
        if self.mode == 0x03:  # MODE_NORMAL
            config += self._t_standby << 5
        if self._iir_filter:
            config += self._iir_filter << 2
        return config

    @property
    def _ctrl_meas(self) -> int:
        """Value to be written to the device's ctrl_meas register"""
        ctrl_meas = self.overscan_temperature << 5
        ctrl_meas += self.overscan_pressure << 2
        ctrl_meas += self.mode
        return ctrl_meas

    @property
    def temperature(self) -> float:
        """The compensated temperature in degrees Celsius."""
        self._read_temperature()
        return self._t_fine

    @property
    def pressure(self) -> float:
        """
        The compensated pressure in hectoPascals.
        """
        self._read_temperature()
        return self._current_forecast["main"]["pressure"]

    @property
    def relative_humidity(self) -> float:
        """
        The relative humidity in RH %
        """
        return self.humidity

    @property
    def humidity(self) -> float:
        """
        The relative humidity in RH %
        """
        self._read_temperature()
        humidity = self._current_forecast["main"]["humidity"]
        if humidity > 100:
            return 100
        if humidity < 0:
            return 0
        return humidity

    @property
    def altitude(self) -> float:
        """The altitude based on current :attr:`pressure` versus the sea level pressure
        (``sea_level_pressure``) - which you must enter ahead of time)"""
        pressure = self.pressure  # in Si units for hPascal
        return 44330 * (1.0 - math.pow(pressure / self.sea_level_pressure, 0.1903))


class Adafruit_BME280_I2C(Adafruit_BME280):
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
        from adafruit_bme280 import basic as adafruit_bme280

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
        address: int = 0x77,  # BME280_ADDRESS
        use_openweather: bool = True,
    ) -> None:
        super().__init__(I2C_Impl(i2c, address), use_openweather=use_openweather)


class Adafruit_BME280_SPI(Adafruit_BME280):
    """Driver for BME280 connected over SPI

    :param ~busio.SPI spi: SPI device
    :param ~digitalio.DigitalInOut cs: Chip Select
    :param int baudrate: Clock rate, default is 100000. Can be changed with :meth:`baudrate`

    .. note::
        The operational range of the BMP280 is 300-1100 hPa.
        Pressure measurements outside this range may not be as accurate.

    **Quickstart: Importing and using the BME280**

        Here is an example of using the :class:`Adafruit_BME280_SPI` class.
        First you will need to import the libraries to use the sensor

        .. code-block:: python

            import board
            from digitalio import DigitalInOut
            from adafruit_bme280 import basic as adafruit_bme280

        Once this is done you can define your `board.SPI` object and define your sensor object

        .. code-block:: python

            cs = digitalio.DigitalInOut(board.D10)
            spi = board.SPI()
            bme280 = adafruit_bme280.Adafruit_BME280_SPI(spi, cs)

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
        spi: SPI,
        cs: DigitalInOut,
        baudrate: int = 100000,
        use_openweather: bool = True,
    ) -> None:
        super().__init__(SPI_Impl(spi, cs, baudrate), use_openweather=use_openweather)
