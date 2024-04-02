Introduction
============




.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord


.. image:: https://github.com/brentru/CircuitPython_Fake_BME280/workflows/Build%20CI/badge.svg
    :target: https://github.com/brentru/CircuitPython_Fake_BME280/actions
    :alt: Build Status


.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Code Style: Black

**This code is for testing purposes only!** If you are looking for a Bosch BME280 driver, please use the `Adafruit_CircuitPython_BME280 <https://github.com/adafruit/Adafruit_CircuitPython_BME280>`_.

This driver mocks the functionality of the `Adafruit_CircuitPython_BME280 <https://github.com/adafruit/Adafruit_CircuitPython_BME280>`_, allowing you to test your code without
attaching physical hardware.

Instead of using random data, weather data is instead pulled from `the OpenWeatherMaps API <https://openweathermap.org/>`_
and returned as if it were coming from the BME280 sensor properties. A free OpenWeatherMap API key is **required** to use this library (see the Usage section below for more information).

Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_
* `Adafruit_CircuitPython_Requests <https://github.com/adafruit/Adafruit_CircuitPython_Requests>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_
or individual libraries can be installed using
`circup <https://github.com/adafruit/circup>`_.

Installing from PyPI
=====================

On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
PyPI <https://pypi.org/project/circuitpython-fake-bme280/>`_.
To install for current user:

.. code-block:: shell

    pip3 install circuitpython-fake-bme280

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install circuitpython-fake-bme280

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .venv
    source .env/bin/activate
    pip3 install circuitpython-fake-bme280

Usage Example
=============

To obtain an OpenWeatherMaps API key, sign up for a free account at `OpenWeatherMaps <https://openweathermap.org/>`_ and generate an API key. Then, in the root of this
project, add a file called "settings.toml" with the following information:

openweather_token = "my_api_key"
openweather_location = "New York, US"
openweather_units = "metric"


Where openweather_token is your OpenWeatherMaps API key, openweather_location is the location you want to pull weather data from, and openweather_units is the units you want the temperature to be returned in (either "metric" or "imperial").

Then, run the code within "examples/fake_bme280.py" to use the "fake" BME280 sensor.

Documentation
=============
API documentation for this library can be found on `Read the Docs <https://circuitpython-fake-bme280.readthedocs.io/>`_.

For information on building library documentation, please check out
`this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/brentru/CircuitPython_Fake_BME280/blob/HEAD/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
