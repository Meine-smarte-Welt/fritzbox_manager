| [🇩🇪<br>**Deutsch**](README.md) | 🇬🇧<br>**English** | [🇳🇱<br>**Nederlands**](README.nl.md) |
|:-:|:-:|:-:|

![FRITZ!Box Manager](docs/images/fritzbox_manager.webp)

# FRITZ!Box Manager

📖 Blog post: [https://meinesmartewelt.de](https://meinesmartewelt.de)

> *Short English version – the complete documentation is the [German README](README.md).*

> **⚠️ Beta (pre-release 0.0.1b0).** This version is **not tested on a real FRITZ!Box**. It was checked against a simulated TR-064 interface and with test data in the browser. Anything depending on real box behaviour is **unverified** (see "Known limitations").

Home Assistant integration with a dashboard card for your FRITZ!Box system data, meant as a replacement for the FRITZ!Box Tools cards. It shows overview, box, internet and Wi-Fi, opens your sibling integrations **FRITZ!Box Anrufe** (calls), **FRITZ!Box Netzwerk** (network) and **FRITZ!Box Ereignisse** (events) as popups, and has a settings tab with version display.

## Features

- Overview, Box (model, firmware, uptime, optional experimental CPU temperature), Internet (status, IPs, rates, traffic, DSL values), Wi-Fi (all networks, popup, switch on/off – admins only, two-click confirm for switching off), Modules (popups of the sibling cards), Settings (version + update hint, options, maintenance, event log).
- Entities: sensors, binary sensors, Wi-Fi switches, buttons (reboot, reconnect).
- Languages: German, English, Dutch.

## What's new in 0.0.1b0

First release (beta).

## Screenshots

All images show **version 0.0.1b0 with test data** (no real FRITZ!Box).

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

Services (admin only): `fritzbox_manager.set_wlan`, `reconnect`, `reboot`, `check_for_update`. Events: `fritzbox_manager_internet_offline`, `_internet_online`, `_ip_changed`, `_update_available`.

## Version display

The version is shown in the card settings, in the card editor and in the options dialog. GitHub is checked every 12 hours (pre-releases included while a beta is installed).

## Security

Write actions are admin-only and validated in the backend; risky actions need two clicks; all card text is escaped; colours are allow-listed; `read_only` hides all controls.

## Known limitations

- **Not tested on real hardware** (simulated TR-064 and browser test data only).
- Guest Wi-Fi and frequency band are heuristics (with 3+ networks the last one counts as guest; band derived from channel; 6 GHz not distinguished).
- No CPU/RAM load; CPU temperature only experimentally via an undocumented interface (off by default).
- English and Dutch are not reviewed by native speakers.
- Popups need the sibling integrations and cards; Notification Center is not connected.

## Version history

| Version | Changes |
|---|---|
| **0.0.1b0** | First release (beta). |

## File integrity

`.py`, `.js` and `.yaml` files carry their SHA256 (content from line 2) in the first line. JSON files:

| File | SHA256 |
|---|---|
| `custom_components/fritzbox_manager/manifest.json` | `022c1b926219685a562217fcd06bd250351ba4cc1c1d7d5223e77034438b1eb2` |
| `custom_components/fritzbox_manager/strings.json` | `8b4f38becb3430565684d940f32e5c7015877cabcd73ae1443a24c8cee764299` |
| `custom_components/fritzbox_manager/icons.json` | `c8d53de9c2e752cc325931793c937d331e948851fe57ce2bbbb5acc49d0ecab4` |
| `custom_components/fritzbox_manager/translations/de.json` | `8b4f38becb3430565684d940f32e5c7015877cabcd73ae1443a24c8cee764299` |
| `custom_components/fritzbox_manager/translations/en.json` | `a27e218de9de4e967205dbbdb1d8d20b24b9f4d81d1fa44fb2ca01bccc52a4e1` |
| `custom_components/fritzbox_manager/translations/nl.json` | `45cd17e4bb7244818ad1abf62eecdf3c972ab2faaeab8f06dde53dd37a7dcaad` |
| `hacs.json` | `360a813ce8c9ed6a42abd57d21c4b416646ffe3fe6777d8fd89145e9ef989a71` |

## License

MIT, see [LICENSE](LICENSE).
