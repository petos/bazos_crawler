import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    DEFAULT_UPDATE_INTERVAL,
    CONF_UPDATE_INTERVAL,
    CONF_SEARCH_TERM,
    CONF_PSC,
    CONF_OKOLI,
    CONF_CENAOD,
    CONF_CENADO,
    CONF_SEARCH_EXACT,
)

def _parse_optional_int(value, field):
    value = (value or "").strip()
    if value == "":
        return ""
    try:
        return int(value)
    except ValueError:
        raise ValueError(field)


def _validate_psc(psc):
    if psc == "":
        return True
    return 10000 <= psc <= 99999


class BazosConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        schema = vol.Schema(
            {
                vol.Required(CONF_SEARCH_TERM): cv.string,
                vol.Optional(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): cv.positive_int,
                vol.Optional(CONF_SEARCH_EXACT, default=True): cv.boolean,
                vol.Optional(CONF_PSC, default=""): cv.string,
                vol.Optional(CONF_OKOLI, default="25"): cv.string,
                vol.Optional(CONF_CENAOD, default=""): cv.string,
                vol.Optional(CONF_CENADO, default=""): cv.string,
            }
        )

        if user_input is not None:
            term = user_input[CONF_SEARCH_TERM].strip()

            try:
                psc = _parse_optional_int(user_input.get(CONF_PSC), CONF_PSC)
                if not _validate_psc(psc):
                    errors[CONF_PSC] = "invalid_psc"
            except ValueError as e:
                errors[e.args[0]] = "invalid_number"
                psc = ""

            try:
                okoli = _parse_optional_int(user_input.get(CONF_OKOLI), CONF_OKOLI)
            except ValueError as e:
                errors[e.args[0]] = "invalid_number"
                okoli = ""

            try:
                cenaod = _parse_optional_int(user_input.get(CONF_CENAOD), CONF_CENAOD)
            except ValueError as e:
                errors[e.args[0]] = "invalid_number"
                cenaod = ""

            try:
                cenado = _parse_optional_int(user_input.get(CONF_CENADO), CONF_CENADO)
            except ValueError as e:
                errors[e.args[0]] = "invalid_number"
                cenado = ""

            if not term:
                errors[CONF_SEARCH_TERM] = "empty"

            if not errors:
                await self.async_set_unique_id(term.lower())
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Bazos: {term}",
                    data={
                        CONF_SEARCH_TERM: term,
                        CONF_UPDATE_INTERVAL: user_input.get(CONF_UPDATE_INTERVAL),
                        CONF_SEARCH_EXACT: user_input.get(CONF_SEARCH_EXACT, True),
                        CONF_PSC: psc,
                        CONF_OKOLI: okoli,
                        CONF_CENAOD: cenaod,
                        CONF_CENADO: cenado,
                    },
                )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
