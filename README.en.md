| [🇩🇪<br>**Deutsch**](README.md) | 🇬🇧<br>**English** | [🇳🇱<br>**Nederlands**](README.nl.md) |
|:-:|:-:|:-:|

![FRITZ!Box Manager](docs/images/fritzbox_manager.webp)

# FRITZ!Box Manager

📖 Blog post: [https://meinesmartewelt.de](https://meinesmartewelt.de)

> *Short English version – the complete documentation is the [German README](README.md).*

> **⚠️ Beta (pre-release 0.0.3b1).** This version is **not tested on a real FRITZ!Box**. It was checked against a simulated TR-064 interface and with test data in the browser. Anything depending on real box behaviour is **unverified** (see "Known limitations").

Home Assistant integration with a dashboard card for your FRITZ!Box system data, meant as a replacement for the FRITZ!Box Tools cards. It shows overview, box, internet and Wi-Fi, opens your sibling integrations **FRITZ!Box Anrufe** (calls), **FRITZ!Box Netzwerk** (network) and **FRITZ!Box Ereignisse** (events) as popups, and has a settings tab with version display.

## Features

- Overview, Box (model, firmware, uptime, optional experimental CPU temperature), Internet (status, IPs, rates, traffic, DSL values), Wi-Fi (all networks, popup, switch on/off – admins only, two-click confirm for switching off), Modules (popups of the sibling cards), Settings (version + update hint, options, maintenance, event log).
- **Backup (experimental, off by default):** trigger a backup of the FRITZ!Box settings and store it in the Home Assistant config folder – see [EXPERIMENTELL.md](EXPERIMENTELL.md) (German).
- Entities: sensors, binary sensors, Wi-Fi switches, buttons (reboot, reconnect).
- Languages: German, English, Dutch.

## What's new in 0.0.3b1

- **New logos** (`brand/`): icon and logo with the new router symbol.
- **Options grouped.** In the options dialog the optional settings (CPU temperature, experimental features, backup, backups to keep) now sit in a **collapsible section** (accordion). In the card they are a sub-section *Optional settings* under *Settings → Options*. Stored options are unchanged.
- **Changed: CPU temperature** is now read from the box's web interface (page `ecoStat`), like *FRITZ!Box Netzwerk*, instead of TR-064. The session is reused so the box does not report a login on every poll. Still experimental and **unverified on a real box in this project**; the parsing comes from the Netzwerk integration, where the value works.
- **Changed: Wi-Fi in HTTP mode.** The Wi-Fi query is more tolerant (only the basic network data is mandatory, extras may be missing) and falls back once to the encrypted interface (port 49443) when the unencrypted query is refused; this also applies to switching. **Cause unconfirmed, change unverified on a real box.** If it does not help, please report the reason shown by the card under *Settings → Connection*.
- Backup (experimental) is unchanged; see [EXPERIMENTELL.md](EXPERIMENTELL.md) (German).

## Screenshots

All images show **version 0.0.1b0 with test data** (no real FRITZ!Box); they have not been regenerated for 0.0.3b1.

| Overview | Wi-Fi popup |
|:-:|:-:|
| ![Overview (test data)](docs/images/overview-en.webp) | ![Wi-Fi popup (test data)](docs/images/wlan-popup.webp) |

*(The Wi-Fi popup screenshot is the German one.)*

## Requirements

Home Assistant 2025.6+, a FRITZ!Box with TR-064 enabled and a user with the needed rights. The popups need the sibling integrations (optional).

## Installation

**HACS:** add `https://github.com/Meine-smarte-Welt/fritzbox_manager` as custom repository (category *Integration*). Because this is a pre-release, enable **"Show beta versions"** for the repository in HACS. Restart Home Assistant.
**Manual:** copy `custom_components/fritzbox_manager` to `config/custom_components/`.

The card is registered as a Lovelace resource automatically (YAML mode: add `/fritzbox_manager_files/fritzbox-manager-card.js` as *module* yourself). Reload the browser (Ctrl+F5).

## Setup and card

*Settings → Devices & services → Add integration → FRITZ!Box Manager.* Card:

```yaml
type: custom:fritzbox-manager-card
```

Keys: `title`, `show_title`, `show_overview|system|internet|wifi|modules|settings`, `default_tab`, `zoom`, `read_only`, `entry_id`, `module_*_config`, `color_*`. See [`examples/`](examples/). Unlike the other managers this card has no column lists, so there is no search, filter, sort or column switches.

## Services and events

Services (admin only): `fritzbox_manager.set_wlan`, `reconnect`, `reboot`, `check_for_update`, `create_backup` (experimental). Events: `fritzbox_manager_internet_offline`, `_internet_online`, `_ip_changed`, `_update_available`, `_backup_created`.

## Version display

The version is shown in the card settings, in the card editor and in the options dialog. GitHub is checked every 12 hours (pre-releases included while a beta is installed).

## Security

Write actions are admin-only and validated in the backend; risky actions need two clicks; all card text is escaped; colours are allow-listed; `read_only` hides all controls.

## Known limitations

- **Not tested on real hardware** (simulated TR-064 and browser test data only).
- Guest Wi-Fi and frequency band are heuristics (with 3+ networks the last one counts as guest; band derived from channel; 6 GHz not distinguished).
- No CPU/RAM load; CPU temperature only experimentally via the box's undocumented web interface (off by default). The user needs web interface access; reasons are shown in the card under *Settings → Connection* (`cpu: web_login` = login rejected, `web_blocked` = login blocked, `web_unreachable` = web interface not reachable, `web_http`/`web_no_data` = unexpected reply).
- **Backup is unverified:** whether the box delivers the backup via TR-064 depends on model, FRITZ!OS, user rights and possibly two-factor confirmation; it may end with an error message. The password is not stored – without it the file cannot be restored on the box. The file format is not validated. Restoring is deliberately done on the box only (*System → Backup*).
- Fibre models have no DSL values (e.g. FRITZ!Box 5690 Pro).
- English and Dutch are not reviewed by native speakers.
- Popups need the sibling integrations and cards; Notification Center is not connected.

## Version history

| Version | Changes |
|---|---|
| **0.0.3b1** | New logos. Optional settings in a collapsible section (options dialog and card). CPU temperature via the web interface (like FRITZ!Box Netzwerk). Wi-Fi more tolerant in HTTP mode, with fallback to the encrypted interface. |
| **0.0.2b1** | Experimental: backup of box settings (service, card, event). DSL zeros on models without DSL shown as "–". Reason shown for an empty Wi-Fi list. |
| **0.0.1b0** | First release (beta). |

## File integrity

`.py`, `.js` and `.yaml` files carry their SHA256 (content from line 2) in the first line. JSON files:

| File | SHA256 |
|---|---|
| `custom_components/fritzbox_manager/manifest.json` | `2a69b0d226133d3065ffe64a5c6aa43a1c3b0bd0bb4f950859603be9d63fe9a7` |
| `custom_components/fritzbox_manager/strings.json` | `cef404d0990ac21bba2f8d3282670023b71abaac4112b43274328f174b99ddea` |
| `custom_components/fritzbox_manager/icons.json` | `b8b33129c6a6251f46d807f220e325b85d5923ec945e91a33b77a1f2f529ce0e` |
| `custom_components/fritzbox_manager/translations/de.json` | `cef404d0990ac21bba2f8d3282670023b71abaac4112b43274328f174b99ddea` |
| `custom_components/fritzbox_manager/translations/en.json` | `8e18df6cdf762fbb005e273e9a6db894624e6269b2b94443d29dbab73e699915` |
| `custom_components/fritzbox_manager/translations/nl.json` | `7665e6a3f05d5fdf3a06ef452c557d49a6a23ce4a6494280b310574fbeb7d8f3` |
| `hacs.json` | `360a813ce8c9ed6a42abd57d21c4b416646ffe3fe6777d8fd89145e9ef989a71` |

## License

MIT, see [LICENSE](LICENSE).
