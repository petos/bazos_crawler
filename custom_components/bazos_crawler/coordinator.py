from datetime import timedelta
from urllib.parse import quote
import logging

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import BazosApi
from .const import (
    DOMAIN,
    BASE_URL,
    CONF_SEARCH_TERM,
    CONF_PSC,
    CONF_OKOLI,
    CONF_CENAOD,
    CONF_CENADO,
    CONF_SEARCH_EXACT,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

def build_url(exact: bool, term: str, psc, okoli, cenaod, cenado):
    if exact:
        term = quote(f'"{term}"', safe="")

    return BASE_URL.format(
        term=term,
        psc=psc or "",
        okoli=okoli or "",
        cenaod=cenaod or "",
        cenado=cenado or "",
    )


class BazosDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, config_entry):
        self.config_entry = config_entry
        session = async_get_clientsession(hass)
        self.api = BazosApi(session)

        update_interval = config_entry.options.get(
            CONF_UPDATE_INTERVAL,
            config_entry.data.get(CONF_UPDATE_INTERVAL),
        ) or DEFAULT_UPDATE_INTERVAL

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval),
        )

    @property
    def url(self):
        data = self.config_entry.data
        options = self.config_entry.options

        return build_url(
            options.get(CONF_SEARCH_EXACT, data.get(CONF_SEARCH_EXACT)),
            data.get(CONF_SEARCH_TERM),
            options.get(CONF_PSC, data.get(CONF_PSC)),
            options.get(CONF_OKOLI, data.get(CONF_OKOLI)),
            options.get(CONF_CENAOD, data.get(CONF_CENAOD)),
            options.get(CONF_CENADO, data.get(CONF_CENADO)),
        )

    async def _async_update_data(self):
        url = self.url

        _LOGGER.debug("Fetching URL: %s", url)

        try:
            return await self.api.fetch(url)
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}") from err
