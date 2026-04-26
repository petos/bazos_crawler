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
 - `Celkem` -- Celkovy počet nalezených inzerátů s daným klíčovym slovem
 - `Dnes` -- Počet přidaných inzerátu dnes
 - `Nové dnes` -- Binární sensor - překlopí se do `True` ve chvíli, kdy najde nový, zatím neviděný inzerát. Při dalším běhu, ve výchozím nastavení 5 minut, se překlopí zpět do `False`. 

### Atributy
 - URL na search do Bazose. 

### Button
 - Je k dispozici i button, ktery otevira URL s hledanim. Je nutne mit nainstalovany browser_mod plugin z HACS, jinak je button zasedly a nepouziva se.

## Konfigurace - UI konfigurace:
- Nastavení > Zařízení a služby > Přidat integraci
  - Hledaný termín: KLÍČ, který chceš vyhledávat
  - Interval aktualizace (s): Jak často se má vyhledávání obnovovat (v sekundách). Výchozí hodnota je 5 minut, NEdoporucuji snižovat pod 60 sekund.
  - Pouze přesná shoda: Hledej pouze *přesnou shodu* -- především v případě mezery mezi slovy se nepočítá "termín_A něco něco termín_B", musí být přesná shoda
  - PSČ: 5místné číslo
  - V okruhu (km): Hledat v okruhu XXX km okolo PSČ. Pokud PSČ není zadané, ignoruje se.
  - Cena OD: Minimální cena
  - Cena DO: Maximální cena
- Automaticky vytvoří senzory
- Aktualizace hodnot probíhá jednou za 5 minut nebo zvolený časový interval.

## Jak najít přímo URL?
Otevřete si podrobnosti libovolného senzoru (klikněte na senzor třeba Total) -> Tři tečky -> Podrobnosti. Dole je mezi atributy je "URL". 

## Hlášení chyb
Nejlépe přes https://github.com/petos/bazos_crawler/issues
