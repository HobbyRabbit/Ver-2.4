from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=30)


class ACInfinityCoordinator(DataUpdateCoordinator[dict]):
    """AC Infinity BLE Coordinator"""

    def __init__(
        self,
        hass: HomeAssistant,
        client,
        address: str,
        ports: int = 8,
    ) -> None:
        self.hass = hass
        self.client = client
        self.address = address
        self.ports = ports

        super().__init__(
            hass,
            _LOGGER,
            name=f"AC Infinity {address}",
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> dict:
        """Fetch data from the AC Infinity device"""

        try:
            # --- CONNECT IF NEEDED ---
            if not self.client.is_connected:
                _LOGGER.debug("Connecting to AC Infinity %s", self.address)
                await self.client.connect()

            # --- BUILD STATE DICT ---
            data: dict = {
                "online": True,
                "ports": {},
            }

            # --- PLACEHOLDER PORT STATE ---
            # We do NOT yet know the real readback format.
            # This keeps HA stable while we reverse packets.
            for port in range(1, self.ports + 1):
                data["ports"][port] = {
                    "state": None,   # unknown yet
                    "speed": None,   # fans use this, outlets ignore
                }

            return data

        except Exception as err:
            _LOGGER.exception(
                "Unexpected error fetching AC Infinity %s data", self.address
            )
            raise UpdateFailed(err) from err
