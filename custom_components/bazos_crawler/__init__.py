from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

import logging

_LOGGER = logging.getLogger(__name__)

from .const import DOMAIN, PLATFORMS, STORAGE_VERSION
from .coordinator import BazosDataUpdateCoordinator

async def async_cleanup_orphan_storage(hass):
    """Remove storage files for deleted config entries."""

    # existující entry_id
    active_entries = {
        entry.entry_id
        for entry in hass.config_entries.async_entries("bazos")
    }

    store = hass.helpers.storage.Store  # jen pro info, ne přímo použití

    # HA interně ukládá storage v hass.data["storage"]
    storage_data = hass.data.get("storage", {}).get("core.config_entries", {})

    removed = 0

    for key in list(storage_data.keys()):
        if not key.startswith(STORAGE_PREFIX):
            continue

        entry_id = key.replace(STORAGE_PREFIX, "")

        if entry_id not in active_entries:
            _LOGGER.warning("Cleaning orphan storage: %s", key)

            # safest generic wipe (HA controlled)
            storage_data.pop(key, None)
            removed += 1

    if removed:
        _LOGGER.info("Cleaned %s orphan storage entries", removed)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = BazosDataUpdateCoordinator(hass, entry)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_delete_storage()

    return unload_ok
