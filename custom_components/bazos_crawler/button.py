from homeassistant.components.button import ButtonEntity

from .const import DOMAIN
from .entity import BazosEntity


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    term = entry.data["search_term"]

    async_add_entities(
        [BazosOpenSearchButton(coordinator, term)],
        True,
    )


class BazosOpenSearchButton(BazosEntity, ButtonEntity):
    def __init__(self, coordinator, term: str):
        super().__init__(coordinator, term)

        self._attr_name = f"Bazos {self._term} otevřít link"
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{self._slug}_open"


    @property
    def available(self) -> bool:
        # button bude "disabled" (greyed out) pokud browser_mod není
        return self.hass.services.has_service("browser_mod", "navigate")

    async def async_press(self):
        url = self.coordinator.url

        if self._browser_mod_available:
            await self.hass.services.async_call(
                "browser_mod",
                "navigate",
                {"url": url},
                blocking=False,
            )
            return

        self.coordinator.logger.warning(
            "browser_mod not available, URL: %s", url
        )
