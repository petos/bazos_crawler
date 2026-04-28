# bazosCrawler

Prochází bazoš každých 5 minut a dle zadaných kritérií (klíčové slovo/a, okolí místa, cena max/min) reportuje změnou binary_sensoru přítomnost nového, zatím neviděného, inzerátu/inzerátů. Následně je pak možné tvořit notifikaci na základě změny stavu, posílat email,...

## Instalace
- Přes HACS

  [![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Petos&repository=bazos_crawler)

  - Nainstalujte HACS
  - V HACS rozhraní kliknout v pravém horním rohu na tři svislé tečky
  - Kliknout na Vlastní repozitáře
  - Přidat adresu `https://github.com/petos/bazos_crawler` a typ `Integrace`
  - Po přidání repozitáře vyhledat `Bazos Crawler` a nainstalovat
  - Po restartu Home Assistenta přidat jako Integraci v Nastavení -> Integrace
- Ručně:
  - Nahrajte obsah `custom_components/bazos_crawler/` do `/config/custom_components/bazos_crawler/`

## Senzory
 - `sensor.bazos_HLEDANY_KLIC_celkem` -- `Celkem` -- Celkovy počet nalezených inzerátů s daným klíčovym slovem
 - `sensor.bazos_HLEDANY_KLIC__dnes` -- `Dnes` -- Počet přidaných inzerátu dnes
 - `binary_sensor.bazos_HLEDANY_KLIC` -- Binární sensor - překlopí se do `True` ve chvíli, kdy najde nový, zatím neviděný inzerát. Při dalším běhu, ve výchozím nastavení 5 minut, se překlopí zpět do `False`. 

### Atributy
 - URL na search do Bazose. 

### Button
 - Je k dispozici i button, ktery otevira URL s hledanim. Je nutne mit nainstalovany browser_mod plugin z HACS, jinak je button zasedly a nepouziva se.

## Konfigurace - UI konfigurace:
- Nastavení > Zařízení a služby > Přidat integraci
  - `Hledaný termín`: KLÍČ, který chceš vyhledávat
  - `Interval aktualizace (s)`: Jak často se má vyhledávání obnovovat (v sekundách). Výchozí hodnota je 5 minut, NEdoporucuji snižovat pod 60 sekund.
  - `Pouze přesná shoda`: Hledej pouze *přesnou shodu* -- především v případě mezery mezi slovy se nepočítá "termín_A něco něco termín_B", musí být přesná shoda
  - `PSČ`: 5místné číslo
  - `V okruhu (km)`: Hledat v okruhu XXX km okolo PSČ. Pokud PSČ není zadané, ignoruje se.
  - `Cena OD`: Minimální cena
  - `Cena DO`: Maximální cena
- Automaticky vytvoří senzory
- Aktualizace hodnot probíhá jednou za 5 minut nebo zvolený časový interval.

## Jak najít přímo URL?
Otevřete si podrobnosti libovolného senzoru (klikněte na senzor třeba Total) -> Tři tečky -> Podrobnosti. Dole je mezi atributy je "URL". 

## Automatizace

### Event: `bazos_new_ads`

Při nalezení nových inzerátů integrace vyvolá event:
```python
self.hass.bus.async_fire(
    "bazos_new_ads",
    {
        "entry_id": "...",
        "term": "octavia",
        "items": [...]
    },
)
```

### Základní trigger

```yaml
alias: Bazos – nové inzeráty
trigger:
  - platform: event
    event_type: bazos_new_ads
```

### Notifikace do mobilu

```yaml
alias: Bazos notifikace
trigger:
  - platform: event
    event_type: bazos_new_ads

action:
  - service: notify.mobile_app_tvuj_telefon
    data:
      title: "Bazos: nové inzeráty"
      message: >
        {% for item in trigger.event.data.items %}
        {{ item.title }} - {{ item.price }} Kč
        {{ item.url }}
        
        {% endfor %}
```

### Filtrování konkrétního search
Pokud máš více searchů:
```yaml
condition:
  - condition: template
    value_template: >
      {{ trigger.event.data.term == "octavia" }}
```


### Jen prvních N inzerátů

```yaml
message: >
  {% for item in trigger.event.data.items[:3] %}
  {{ item.title }} - {{ item.price }} Kč
  {{ item.url }}
  
  {% endfor %}

```
###  Anti-spam (doporučeno)
```yaml
mode: single
max_exceeded: silent
```
nebo delay:
```yaml
action:
  - delay: "00:00:10"
```
###  Poznámky

-   První běh → všechny inzeráty jsou „nové“
-   Při změně filtru se historie resetuje
-   Při odstranění integrace se storage smaže

###  Příklad payloadu eventu

```yaml
event_type: bazos_new_ads
data:
  entry_id: "01KQ..."
  term: "octavia"
  items:
    - title: "Škoda Octavia RS"
      price: 250000
      link: "https://..."

```


## Hlášení chyb
Nejlépe přes https://github.com/petos/bazos_crawler/issues
