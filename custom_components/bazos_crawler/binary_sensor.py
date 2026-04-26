from datetime import datetime

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .entity import BazosEntity

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    term = entry.data["search_term"]

    async_add_entities([
        BazosNewTodayBinarySensor(coordinator, term)
    ])


class BazosNewTodayBinarySensor(BazosEntity, BinarySensorEntity):
    def __init__(self, coordinator, term):
        super().__init__(coordinator, term)
        self._seen_ids = set()
        self._triggered = False

    def _is_today(self, item):
        return item.get("date") == datetime.now().date()

    @property
    def is_on(self):
        items = self.coordinator.data.get("items", [])

        current_ids = {i["id"] for i in items if "id" in i}
        new_ids = current_ids - self._seen_ids

        self._seen_ids.update(current_ids)

        new_today = any(
            i["id"] in new_ids and self._is_today(i)
            for i in items
        )

        if new_today:
            self._triggered = True
            return True

        if self._triggered:
            self._triggered = False
            return False

        return False

    @property
    def unique_id(self):
        return f"{DOMAIN}_{self._slug}_new_today"
