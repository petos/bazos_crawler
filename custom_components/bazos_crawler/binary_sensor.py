from homeassistant.components.binary_sensor import BinarySensorEntity

from .const import DOMAIN
from .entity import BazosEntity


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    term = entry.data["search_term"]

    async_add_entities([
        BazosNewItemsBinarySensor(coordinator, term)
    ])


class BazosNewItemsBinarySensor(BazosEntity, BinarySensorEntity):
    @property
    def name(self):
        return f"Bazos {self._term} nové inzeráty"

    @property
    def unique_id(self):
        return f"{self.coordinator.config_entry.entry_id}_new"

    @property
    def is_on(self):
        return self.coordinator.data.get("new_count", 0) > 0

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data or {}
        new_items = data.get("new_items", [])

        # limit kvůli HA (doporučeno)
        new_items = new_items[:10]

        return {
            "new_count": data.get("new_count", 0),
            "new_items": [
                {
                    "title": item["title"],
                    "price": item["price"],
                    "url": item["link"],
                }
                for item in new_items
            ],
        }
