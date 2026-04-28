from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    CONF_SEARCH_TERM,
    CONF_SEARCH_EXACT,
    CONF_PSC,
    CONF_OKOLI,
    CONF_CENAOD,
    CONF_CENADO,
)


class BazosEntity(CoordinatorEntity):
    def __init__(self, coordinator, term):
        super().__init__(coordinator)
        self._term = term

    # -------------------------
    # DEVICE NAME BUILDER
    # -------------------------
    def _build_device_name(self):
        data = self.coordinator.config_entry.data
        options = self.coordinator.config_entry.options

        term = data.get(CONF_SEARCH_TERM)

        exact = options.get(CONF_SEARCH_EXACT, data.get(CONF_SEARCH_EXACT))
        psc = options.get(CONF_PSC, data.get(CONF_PSC))
        okoli = options.get(CONF_OKOLI, data.get(CONF_OKOLI))
        cenaod = options.get(CONF_CENAOD, data.get(CONF_CENAOD))
        cenado = options.get(CONF_CENADO, data.get(CONF_CENADO))

        parts = []

        # search term
        parts.append(term)

        # location
        if psc:
            if okoli:
                parts.append(f"{psc} ±{okoli}km")
            else:
                parts.append(f"{psc}")
        else:
            parts.append("ALL location")

        # price
        price = self._fmt_range(cenaod, cenado, "Kč")
        if price:
            parts.append(price)
        else:
            parts.append("cena ALL")

        # exact
        if exact:
            parts.append("exact")

        return "Bazos: " + " | ".join(str(p) for p in parts if p)

    # -------------------------
    # DEVICE INFO
    # -------------------------
    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.coordinator.config_entry.entry_id)},
            "name": self._build_device_name(),
            "manufacturer": "BazosCrawler",
            "model": "Search",
        }

    # -------------------------
    # ATTRIBUTES
    # -------------------------
    @property
    def extra_state_attributes(self):
        return {
            "search_url": self.coordinator.url
        }

    # -------------------------
    # UNIQUE ID (stabilní!)
    # -------------------------
    @property
    def unique_id(self):
        return f"{self.coordinator.config_entry.entry_id}_"

    def _fmt_range(self, a, b, suffix=""):
        a = self._fmt_price(a)
        b = self._fmt_price(b)

        if a or b:
            return f"{a or '0'}–{b or '∞'} {suffix}".strip()
        return None

    def _fmt_price(self, val):
        if not val:
            return None
        val = int(val)
        if val >= 1000:
            return f"{val//1000}k"
        return str(val)
