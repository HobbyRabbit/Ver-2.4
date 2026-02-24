from homeassistant.components.number import NumberEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

PORTS = 8


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        ACInfinityPortSpeed(coordinator, i)
        for i in range(PORTS)
    ]

    async_add_entities(entities)


class ACInfinityPortSpeed(CoordinatorEntity, NumberEntity):
    _attr_native_min_value = 0
    _attr_native_max_value = 10
    _attr_native_step = 1

    def __init__(self, coordinator, index):
        super().__init__(coordinator)
        self.index = index
        self._attr_name = f"AC Infinity Port {index+1} Speed"

    @property
    def native_value(self):
        return self.coordinator.data["speed"][self.index]

    async def async_set_native_value(self, value):
        await self.coordinator.set_speed(self.index, int(value))
        await self.coordinator.async_request_refresh()
