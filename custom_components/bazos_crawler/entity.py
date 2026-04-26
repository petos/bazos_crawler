from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN,CONF_SEARCH_EXACT


class BazosEntity(CoordinatorEntity):
    def __init__(self, coordinator, term):
        super().__init__(coordinator)
        self._term = term
        self._slug = "".join(c.lower() if c.isalnum() else "_" for c in term)

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.coordinator.config_entry.entry_id)},
            "name": f"Bazos {self._term}",
            "manufacturer": "BazosCrawler",
            "model": "Search",
        }

    # ~ @property
    # ~ def extra_state_attributes(self):
        # ~ return "exact": self.coordinator.CONF_SEARCH_EXACT

    @property
    def extra_state_attributes(self):
        url = self.coordinator.url
        return {
            "search_url": url,
            "search_link": f"[Open Bazos]({url})"
        }

    @property
    def unique_id(self):
        return f"{self.coordinator.config_entry.entry_id}_{self._slug}"
