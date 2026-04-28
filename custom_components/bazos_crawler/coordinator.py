from datetime import timedelta, datetime
from urllib.parse import quote
import logging

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.storage import Store

from .api import BazosApi
from .const import (
    DOMAIN,
    BASE_URL,
    STORAGE_VERSION,
    STORAGE_PREFIX,
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

        # --- STORAGE (per entry) ---
        self.storage_key = f"{STORAGE_PREFIX}{config_entry.entry_id}"
        self.store = Store(hass, STORAGE_VERSION, self.storage_key)

        self.seen_ads = {}
        self._initialized = False

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

    # -------------------------
    # STORAGE HELPERS
    # -------------------------
    async def _load_seen(self):
        data = await self.store.async_load()

        if data:
            stored_url = data.get("meta", {}).get("url")

            # pokud se změnil search, reset
            if stored_url != self.url:
                _LOGGER.debug("Search changed, resetting seen ads")
                self.seen_ads = {}
            else:
                self.seen_ads = data.get("seen", {})
        else:
            self.seen_ads = {}

        _LOGGER.debug("Loaded seen ads: %s", len(self.seen_ads))

    async def _save_seen(self):
        await self.store.async_save({
            "meta": {
                "url": self.url,
            },
            "seen": self.seen_ads,
        })

    # -------------------------
    # MAIN UPDATE LOOP
    # -------------------------
    async def _async_update_data(self):
        url = self.url

        _LOGGER.debug("Fetching URL: %s", url)

        try:
            # load pouze jednou po startu
            if not self._initialized:
                await self._load_seen()
                self._initialized = True

            #SNAPSHOT před update
            previous_ids = set(self.seen_ads.keys())

            data = await self.api.fetch(url)
            items = data.get("items", [])

            now = datetime.utcnow().isoformat()

            current_ids = set()
            new_items = []

            for item in items:
                ad_id = item["id"]
                current_ids.add(ad_id)

                #DETEKCE NOVYHO
                if ad_id not in previous_ids:
                    new_items.append(item)

                #update persistence
                if ad_id not in self.seen_ads:
                    self.seen_ads[ad_id] = {
                        "url": item["link"],
                        "title": item["title"],
                        "price": item["price"],
                        "last_seen": now,
                    }
                else:
                    self.seen_ads[ad_id]["last_seen"] = now

            if new_items:
                self.hass.bus.async_fire(
                    "bazos_new_ads",
                    {
                        "entry_id": self.config_entry.entry_id,
                        "term": self.config_entry.data.get("search_term"),
                        "items": new_items,
                    },
                )

            # odstranění smazaných inzerátů
            to_delete = [
                ad_id for ad_id in self.seen_ads
                if ad_id not in current_ids
            ]

            for ad_id in to_delete:
                del self.seen_ads[ad_id]

            if to_delete:
                _LOGGER.debug("Removed %s stale ads", len(to_delete))

            _LOGGER.debug(
                "Seen total=%s current=%s new=%s",
                len(self.seen_ads),
                len(current_ids),
                len(new_items),
            )

            # uložit stav
            await self._save_seen()

            #ROZŠÍŘENÍ DAT PRO HA
            data["new_items"] = new_items
            data["new_count"] = len(new_items)

            return data

        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}") from err

    async def async_delete_storage(self):
        self.seen_ads = {}

        await self.store.async_save({
            "meta": {},
            "seen": {}
        })
