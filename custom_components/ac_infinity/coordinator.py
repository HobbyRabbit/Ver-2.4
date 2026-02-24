from __future__ import annotations

import logging
from datetime import timedelta

from bleak import BleakClient
from bleak_retry_connector import establish_connection

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.components.bluetooth import async_get_scanner

DOMAIN = "ac_infinity"
_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=60)


class ACInfinityCoordinator(DataUpdateCoordinator):
    """Coordinator for AC Infinity BLE device."""

    def __init__(
        self,
        hass: HomeAssistant,
        address: str,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"AC Infinity {address}",
            update_interval=SCAN_INTERVAL,
        )

        self.hass = hass
        self.address = address
        self.client: BleakClient | None = None

    async def _ensure_connected(self) -> None:
        """Ensure BLE connection using HA-safe retry connector."""

        if self.client and self.client.is_connected:
            return

        _LOGGER.debug("Establishing BLE connection to %s", self.address)

        try:
            self.client = await establish_connection(
                BleakClient,
                self.address,
                name=f"ac_infinity_{self.address}",
                scanner=async_get_scanner(self.hass),
            )

            _LOGGER.info("Connected to AC Infinity device %s", self.address)

        except Exception as err:
            self.client = None
            raise UpdateFailed(f"BLE connection failed: {err}") from err

    async def _async_update_data(self) -> dict:
        """Minimal poll — proves BLE connection works."""

        await self._ensure_connected()

        return {
            "connected": True,
            "address": self.address,
        }

    async def async_shutdown(self) -> None:
        if self.client and self.client.is_connected:
            await self.client.disconnect()
            _LOGGER.debug("Disconnected BLE device %s", self.address)
