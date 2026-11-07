| [🇩🇪<br>**Deutsch**](README.md) | [🇬🇧<br>**English**](README.en.md) | 🇳🇱<br>**Nederlands** |
|:-:|:-:|:-:|

![FRITZ!Box Manager](docs/images/fritzbox_manager.webp)

# FRITZ!Box Manager

📖 Blogartikel: [https://meinesmartewelt.de](https://meinesmartewelt.de)

> *Verkorte Nederlandse versie – de volledige documentatie is de [Duitse README](README.md).*

> **Teststatus:** Gecontroleerd met een gesimuleerde TR-064-interface en met testgegevens in de browser. Waarden, eenheden en diensten van andere FRITZ!Box-modellen en FRITZ!OS-versies kunnen afwijken (zie "Bekende beperkingen").

Home Assistant-integratie met dashboardkaart voor de systeemgegevens van je FRITZ!Box, bedoeld als vervanging van de kaarten rond FRITZ!Box Tools. De kaart toont overzicht, box, internet en wifi, opent je zusterintegraties **FRITZ!Box Anrufe** (gesprekken), **FRITZ!Box Netzwerk** (netwerk) en **FRITZ!Box Ereignisse** (gebeurtenissen) als popup en heeft een instellingentab met versieweergave.

## Functies

- Overzicht (kaartjes voor Internet, Download, Upload, Wifi, Box, dataverkeer, DSL en snelle toegang – **elk kaartje is apart in of uit te schakelen**, bijv. DSL bij glasvezel), Box (model, firmware, uptime, optioneel experimentele CPU-temperatuur), Internet (status, IP's, snelheden, dataverkeer, DSL-waarden), Wifi (alle netwerken, popup, in-/uitschakelen – alleen beheerders, uitschakelen met bevestiging in twee klikken), Modules (popups van de zusterkaarten), Instellingen (versie + updatemelding, opties, onderhoud, gebeurtenissenlogboek).
- **Back-up (experimenteel, standaard uit):** een back-up van de FRITZ!Box-instellingen starten en opslaan in de Home Assistant-configuratiemap – zie [EXPERIMENTELL.md](EXPERIMENTELL.md) (Duits).
- Entiteiten: sensoren, binaire sensoren, wifi-schakelaars, knoppen (herstart, opnieuw verbinden).
- Talen: Duits, Engels, Nederlands.

## Nieuw in 0.5.0

Eerste openbare versie.

- **Kaartjes apart schakelbaar.** Elk kaartje van het overzicht heeft een eigen schakelaar (`show_tile_*`). Zonder DSL (bijv. glasvezel) schakel je *DSL-lijn* uit; de DSL-waarden verdwijnen dan ook uit de categorie *Internet*.
- **Kaarteditor als accordeon.** Categorieën zijn inklapbare onderdelen in de editor; kaartjes en modules staan in hun categorie.
- **Opties gebundeld.** Optionele instellingen (CPU-temperatuur, experimentele functies, back-up, aantal back-ups) staan in een inklapbaar onderdeel in het optiesdialoogvenster en in de kaart (*Instellingen → Opties*).
- **Wifi in HTTP-modus** toleranter: alleen de basisgegevens zijn verplicht; wordt de onversleutelde opvraging geweigerd, dan wordt eenmalig de versleutelde interface (poort 49443) gebruikt, ook bij het schakelen. **Niet getest met een echte box**, oorzaak niet bevestigd. Helpt het niet, meld dan de reden onder *Instellingen → Verbinding*.
- **CPU-temperatuur** (experimenteel, uit) wordt net als bij *FRITZ!Box Netzwerk* via de webinterface van de box gelezen. **Back-up** van boxinstellingen (experimenteel, uit): zie [EXPERIMENTELL.md](EXPERIMENTELL.md) (Duits).
- Glasvezelmodellen zonder DSL tonen "–" in plaats van nullen, en bij een lege wifi-lijst noemt de kaart de reden.

## Schermafbeeldingen

Alle afbeeldingen tonen **testgegevens** (geen echte FRITZ!Box). Het onderdeel *Experimenteel* en de kaarteditor staan er niet op.

| Overzicht | Wifi-popup |
|:-:|:-:|
| ![Overzicht (testgegevens)](docs/images/overview-en.webp) | ![Wifi-popup (testgegevens)](docs/images/wlan-popup.webp) |

*(De schermafbeeldingen zijn in het Engels resp. Duits.)*

## Vereisten

Home Assistant 2025.6+, een FRITZ!Box met TR-064 en een gebruiker met de nodige rechten. De popups vereisen de zusterintegraties (optioneel).

## Installatie

**HACS:** voeg `https://github.com/Meine-smarte-Welt/fritzbox_manager` toe als aangepaste repository (categorie *Integratie*). Herstart Home Assistant.
**Handmatig:** kopieer `custom_components/fritzbox_manager` naar `config/custom_components/`.

De kaart wordt automatisch als Lovelace-resource geregistreerd (YAML-modus: voeg `/fritzbox_manager_files/fritzbox-manager-card.js` zelf toe als *module*). Herlaad de browser (Ctrl+F5).

## Instellen en kaart

*Instellingen → Apparaten & diensten → Integratie toevoegen → FRITZ!Box Manager.* Kaart:

```yaml
type: custom:fritzbox-manager-card
```

Sleutels: `title`, `show_title`, `show_overview|system|internet|wifi|modules|settings`, `show_tile_internet|download|upload|wifi|box|traffic|dsl|quick`, `default_tab`, `zoom`, `read_only`, `entry_id`, `module_*_config`, `color_*`. Zie [`examples/`](examples/). In tegenstelling tot de andere managers heeft deze kaart geen kolomlijsten en dus geen zoeken, filteren, sorteren of kolomschakelaars.

### Kaartjes in- en uitschakelen

Het overzicht bestaat uit kaartjes. Elk kaartje kan apart worden uitgeschakeld, in de grafische editor onder **Overzicht** of in YAML:

```yaml
type: custom:fritzbox-manager-card
show_tile_dsl: false      # geen DSL-waarden (overzicht en categorie "Internet"), bijv. bij glasvezel
show_tile_quick: false    # geen snelle toegang
```

Sleutels: `show_tile_internet`, `show_tile_download`, `show_tile_upload`, `show_tile_wifi`, `show_tile_box`, `show_tile_traffic`, `show_tile_dsl`, `show_tile_quick` (standaard `true`). `show_tile_dsl` verbergt de DSL-waarden ook in de categorie *Internet*. Staan alle kaartjes uit, dan toont het overzicht een melding.

### Kaarteditor

In de grafische editor zijn de categorieën samengevat als **inklapbare onderdelen (accordeon)**: *Overzicht* (met de kaartjes), *Box*, *Internet*, *Wifi*, *Modules* (met de modules) en *Instellingen*, daarna *Darstellung* (weergave), *Bearbeiten* (bewerken), *Experimentell* en *Farben* (kleuren). De editorlabels zijn Duits.

## Services en gebeurtenissen

Services (alleen beheerders): `fritzbox_manager.set_wlan`, `reconnect`, `reboot`, `check_for_update`, `create_backup` (experimenteel). Gebeurtenissen: `fritzbox_manager_internet_offline`, `_internet_online`, `_ip_changed`, `_update_available`, `_backup_created`.

## Versieweergave

De versie staat in de kaartinstellingen, in de kaarteditor en in het optiesvenster. GitHub wordt elke 12 uur gecontroleerd.

## Beveiliging

Schrijfacties alleen voor beheerders en in de backend gecontroleerd; riskante acties vragen twee klikken; alle kaarttekst wordt ge-escaped; kleuren via allowlist; `read_only` verbergt alle bediening.

## Bekende beperkingen

- **Beperkte praktijktest.** Geautomatiseerde tests gebruiken een gesimuleerde TR-064-interface en testgegevens in de browser. Waarden, eenheden en diensten van andere FRITZ!Box-modellen en FRITZ!OS-versies zijn niet gecontroleerd; meld afwijkingen als issue.
- Gast-wifi en frequentieband zijn heuristieken (bij 3+ netwerken geldt het laatste als gast; band afgeleid van het kanaal; 6 GHz niet onderscheiden).
- Geen CPU-/RAM-belasting; CPU-temperatuur alleen experimenteel via de niet-openbare webinterface van de box (standaard uit). De gebruiker heeft toegang tot de webinterface nodig; redenen staan in de kaart onder *Instellingen → Verbinding* (`cpu: web_login` = aanmelding geweigerd, `web_blocked` = aanmelding geblokkeerd, `web_unreachable` = webinterface niet bereikbaar, `web_http`/`web_no_data` = onverwacht antwoord).
- **Back-up is niet gecontroleerd:** of de box de back-up via TR-064 levert, hangt af van model, FRITZ!OS, gebruikersrechten en eventueel tweefactorbevestiging; het kan met een foutmelding eindigen. Het wachtwoord wordt niet opgeslagen – zonder kan het bestand niet op de box worden hersteld. Het bestandsformaat wordt niet gevalideerd. Herstellen gebeurt bewust alleen op de box zelf (*Systeem → Back-up*).
- Glasvezelmodellen hebben geen DSL-waarden (bijv. FRITZ!Box 5690 Pro).
- Engels en Nederlands zijn niet door moedertaalsprekers gecontroleerd.
- Popups vereisen de zusterintegraties en -kaarten; Notification Center is niet gekoppeld.

## Versiegeschiedenis

| Versie | Wijzigingen |
|---|---|
| **0.5.0** | Eerste openbare versie: integratie, kaart met 6 categorieën, kaartjes van het overzicht apart schakelbaar, kaarteditor met accordeon, module-popups, wifi schakelen, versieweergave, opties in een inklapbaar onderdeel. Experimenteel (uit): back-up, CPU-temperatuur. |

## Bestandsintegriteit

`.py`-, `.js`- en `.yaml`-bestanden dragen hun SHA256 (inhoud vanaf regel 2) in de eerste regel. JSON-bestanden:

| Bestand | SHA256 |
|---|---|
| `custom_components/fritzbox_manager/manifest.json` | `5236c419705c4d9b77cb1eb2ab6a97d3c208398096ada0de58968dc3e0b97fa6` |
| `custom_components/fritzbox_manager/strings.json` | `cef404d0990ac21bba2f8d3282670023b71abaac4112b43274328f174b99ddea` |
| `custom_components/fritzbox_manager/icons.json` | `b8b33129c6a6251f46d807f220e325b85d5923ec945e91a33b77a1f2f529ce0e` |
| `custom_components/fritzbox_manager/translations/de.json` | `cef404d0990ac21bba2f8d3282670023b71abaac4112b43274328f174b99ddea` |
| `custom_components/fritzbox_manager/translations/en.json` | `8e18df6cdf762fbb005e273e9a6db894624e6269b2b94443d29dbab73e699915` |
| `custom_components/fritzbox_manager/translations/nl.json` | `7665e6a3f05d5fdf3a06ef452c557d49a6a23ce4a6494280b310574fbeb7d8f3` |
| `hacs.json` | `360a813ce8c9ed6a42abd57d21c4b416646ffe3fe6777d8fd89145e9ef989a71` |

## Licentie

MIT, zie [LICENSE](LICENSE).
