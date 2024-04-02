# SPDX-FileCopyrightText: 2022 Randall Bohn (dexter)
#
# SPDX-License-Identifier: MIT
"Provides the protocol objects for I2C and SPI"

from busio import I2C, SPI
from digitalio import DigitalInOut


class I2C_Impl:
    "Protocol implementation for the I2C bus."

    # pylint: disable=too-few-public-methods
    def __init__(self, i2c: I2C, address: int) -> None:
        from adafruit_bus_device import (  # pylint: disable=import-outside-toplevel
            i2c_device,
        )

        self._i2c = i2c_device.I2CDevice(i2c, address)


class SPI_Impl:
    """Protocol implemenation for the SPI bus."""

    # pylint: disable=too-few-public-methods
    def __init__(
        self,
        spi: SPI,
        chip_select: DigitalInOut,
        baudrate: int = 100000,
    ) -> None:
        from adafruit_bus_device import (  # pylint: disable=import-outside-toplevel
            spi_device,
        )

        self._spi = spi_device.SPIDevice(spi, chip_select, baudrate=baudrate)
