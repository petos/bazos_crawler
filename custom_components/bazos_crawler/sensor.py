from homeassistant.components.sensor import SensorEntity, SensorStateClass, SensorDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from datetime import date, datetime


from .const import DOMAIN
from .entity import BazosEntity

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    term = entry.data["search_term"]

    async_add_entities(
        [
            BazosTotalSensor(coordinator, term),
            BazosTodaySensor(coordinator, term),
        ]
    )

class BazosTotalSensor(BazosEntity, SensorEntity):
    @property
    def name(self):
        return f"Bazos {self._term} celkem"

    @property
    def unique_id(self):
        return f"{DOMAIN}_{self._slug}_total"

    @property
    def native_value(self):
        return len(self.coordinator.data.get("items", []))

    @property
    def state_class(self):
        return SensorStateClass.MEASUREMENT

    @property
    def icon(self):
        return "mdi:counter"



class BazosTodaySensor(BazosEntity, SensorEntity):
    @property
    def name(self):
        return f"Bazos {self._term} dnes"

    @property
    def unique_id(self):
        return f"{DOMAIN}_{self._slug}_today"

    @property
    def native_value(self):
        items = self.coordinator.data.get("items", [])
        today = date.today()

        count = 0

        for i in items:
            d = i.get("date")

            if isinstance(d, datetime):
                d = d.date()

            if d == today:
                count += 1

        return count

    @property
    def state_class(self):
        return SensorStateClass.MEASUREMENT

    @property
    def icon(self):
        return "mdi:counter"
