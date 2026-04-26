DOMAIN = "bazos_crawler"
BASE_URL = "https://www.bazos.cz"

DEFAULT_UPDATE_INTERVAL = 300 #in seconds, 5 min.
PLATFORMS = ["sensor", "binary_sensor", "button"]

BASE_URL = "https://www.bazos.cz/search.php?hledat={term}&hlokalita={psc}&humkreis={okoli}&cenaod={cenaod}&cenado={cenado}"

CONF_SEARCH_TERM = "search_term"
CONF_PSC = "search_psc"
CONF_OKOLI = "search_okoli"
CONF_CENAOD = "search_cenaod"
CONF_CENADO = "search_cenado"
CONF_SEARCH_EXACT = "search_exact"

CONF_UPDATE_INTERVAL = "update_interval"
