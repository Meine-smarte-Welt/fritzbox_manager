| [🇩🇪<br>**Deutsch**](README.md) | 🇬🇧<br>**English** | [🇳🇱<br>**Nederlands**](README.nl.md) |
|:-:|:-:|:-:|

![FRITZ!Box Manager](docs/images/fritzbox_manager.webp)

# FRITZ!Box Manager

📖 Blog post: [https://meinesmartewelt.de](https://meinesmartewelt.de)

> *Short English version – the complete documentation is the [German README](README.md).*

> **⚠️ Beta (pre-release 0.0.2b1).** This version is **not tested on a real FRITZ!Box**. It was checked against a simulated TR-064 interface and with test data in the browser. Anything depending on real box behaviour is **unverified** (see "Known limitations").

Home Assistant integration with a dashboard card for your FRITZ!Box system data, meant as a replacement for the FRITZ!Box Tools cards. It shows overview, box, internet and Wi-Fi, opens your sibling integrations **FRITZ!Box Anrufe** (calls), **FRITZ!Box Netzwerk** (network) and **FRITZ!Box Ereignisse** (events) as popups, and has a settings tab with version display.

## Features

- Overview, Box (model, firmware, uptime, optional experimental CPU temperature), Internet (status, IPs, rates, traffic, DSL values), Wi-Fi (all networks, popup, switch on/off – admins only, two-click confirm for switching off), Modules (popups of the sibling cards), Settings (version + update hint, options, maintenance, event log).
- **Backup (experimental, off by default):** trigger a backup of the FRITZ!Box settings and store it in the Home Assistant config folder – see [EXPERIMENTELL.md](EXPERIMENTELL.md) (German).
- Entities: sensors, binary sensors, Wi-Fi switches, buttons (reboot, reconnect).
- Languages: German, English, Dutch.

## What's new in 0.0.2b1

- **Experimental: backup.** Settings → *Experimental*: the card triggers a backup of the FRITZ!Box settings via TR-064 (with a password you choose) and saves the file to `config/fritzbox_manager_backups/`. Admins only, two switches (master switch *Experimental features* and *Backup*), both off by default; the password is neither stored nor logged. **Not tested on a real box.**
- **Fixed: DSL values "0".** If the box has no DSL link (e.g. fibre models), the card shows "–" with a hint instead of zeros.
- **Easier to diagnose: empty Wi-Fi list.** If the box cannot deliver the Wi-Fi networks, the card names the reason (e.g. missing user rights). The actual cause of the reported case is **unconfirmed**; please check the user's right "FRITZ!Box settings".
- New: service `fritzbox_manager.create_backup`, event `fritzbox_manager_backup_created`, options *Experimental features*, *Backup*, *Backups to keep*.

## Screenshots

All images show **version 0.0.1b0 with test data** (no real FRITZ!Box); they have not been regenerated for 0.0.2b1.

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
- No CPU/RAM load; CPU temperature only experimentally via an undocumented interface (off by default).
- **Backup is unverified:** whether the box delivers the backup via TR-064 depends on model, FRITZ!OS, user rights and possibly two-factor confirmation; it may end with an error message. The password is not stored – without it the file cannot be restored on the box. The file format is not validated. Restoring is deliberately done on the box only (*System → Backup*).
- Fibre models have no DSL values (e.g. FRITZ!Box 5690 Pro).
- English and Dutch are not reviewed by native speakers.
- Popups need the sibling integrations and cards; Notification Center is not connected.

## Version history

| Version | Changes |
|---|---|
| **0.0.2b1** | Experimental: backup of box settings (service, card, event). DSL zeros on models without DSL shown as "–". Reason shown for an empty Wi-Fi list. |
| **0.0.1b0** | First release (beta). |

## File integrity

`.py`, `.js` and `.yaml` files carry their SHA256 (content from line 2) in the first line. JSON files:

| File | SHA256 |
|---|---|
| `custom_components/fritzbox_manager/manifest.json` | `918064437ac1fb636b047a4648260b195759b016aab65f9d941bb2bd89aba937` |
| `custom_components/fritzbox_manager/strings.json` | `0d86ec24f652e4db9d9df83aa7006bd0af0b84d4ee667a6318aaabdb50021e4b` |
| `custom_components/fritzbox_manager/icons.json` | `b8b33129c6a6251f46d807f220e325b85d5923ec945e91a33b77a1f2f529ce0e` |
| `custom_components/fritzbox_manager/translations/de.json` | `0d86ec24f652e4db9d9df83aa7006bd0af0b84d4ee667a6318aaabdb50021e4b` |
| `custom_components/fritzbox_manager/translations/en.json` | `ceaf72b1ea6eb5f076248f7130846f53e3a74be7f75e48aeefdef061f13ede76` |
| `custom_components/fritzbox_manager/translations/nl.json` | `4f449f35bcc4c4e822f2282b7316e200456a004af1cbe11025e09f1002c8f7ff` |
| `hacs.json` | `360a813ce8c9ed6a42abd57d21c4b416646ffe3fe6777d8fd89145e9ef989a71` |

## License

MIT, see [LICENSE](LICENSE).
