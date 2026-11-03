| 🇩🇪<br>**Deutsch** | [🇬🇧<br>**English**](README.en.md) | [🇳🇱<br>**Nederlands**](README.nl.md) |
|:-:|:-:|:-:|

![FRITZ!Box Manager](docs/images/fritzbox_manager.webp)

# FRITZ!Box Manager

📖 Blogbeitrag: [https://meinesmartewelt.de](https://meinesmartewelt.de)

> **⚠️ Beta (Pre-release 0.0.2b1).** Diese Version ist **nicht an einer echten FRITZ!Box getestet**. Sie wurde gegen eine simulierte TR-064-Schnittstelle und mit Testdaten im Browser geprüft. Alles, was das Verhalten einer echten Box betrifft, ist **ungeprüft** (siehe „Bekannte Einschränkungen“).

Home-Assistant-Integration mit Dashboard-Karte für die Systemdaten deiner FRITZ!Box – als Ersatz für die Karten rund um FRITZ!Box Tools. Die Karte zeigt Übersicht, Box, Internet und WLAN, öffnet deine Schwester-Integrationen **FRITZ!Box Anrufe**, **FRITZ!Box Netzwerk** und **FRITZ!Box Ereignisse** als Popup und hat einen Einstellungs-Tab mit Versionsanzeige.
<p>
  <a href="https://my.home-assistant.io/redirect/hacs_repository/?owner=Meine-smarte-Welt&amp;repository=fritzbox_manager&amp;category=integration"><img src="https://my.home-assistant.io/badges/hacs_repository.svg" alt="Repository in Home Assistant öffnen" height="32"></a>
</p>
## Funktionsumfang

- **Übersicht:** Internet-Status, Download/Upload, WLAN, Box, Datenmenge, DSL-Werte, Schnellzugriff auf die Module.
- **Box:** Modell, Firmware (inkl. Hinweis auf verfügbares Update), Hardware, Laufzeit, bekannte Netzwerkgeräte, optional CPU-Temperatur (experimentell).
- **Internet:** Verbindungsstatus, Laufzeit, externe IPv4/IPv6, IPv6-Präfix, Leitungsraten, Datenmenge, letzter Fehler, DSL-Werte.
- **WLAN:** alle Funknetze mit Kanal, Standard, Geräten; Popup mit Details; Netze ein-/ausschalten (nur Administratoren, Ausschalten mit Zwei-Klick-Bestätigung).
- **Module:** Popups, die die Karten deiner Integrationen *FRITZ!Box Anrufe*, *Netzwerk* und *Ereignisse* einbetten. Entitäten werden automatisch erkannt; von Hand festlegbar.
- **Einstellungen:** App-Version mit Update-Hinweis, Verbindung, Optionen (Intervall, Ereignisse, CPU-Temperatur), Wartung (Neu verbinden, Neustart – Zwei-Klick), Ereignisprotokoll.
- **Backup (experimentell, standardmäßig aus):** Sicherung der FRITZ!Box-Einstellungen anstoßen und im Home-Assistant-Konfigurationsordner speichern – siehe [EXPERIMENTELL.md](EXPERIMENTELL.md).
- Entitäten: Sensoren, Binärsensoren, WLAN-Schalter, Schaltflächen (Neustart, Neu verbinden).
- Sprachen: Deutsch, Englisch, Niederländisch.

## Neu in 0.0.2b1

- **Experimentell: Backup.** Einstellungen → *Experimentell*: Die Karte stößt über TR-064 eine Sicherung der FRITZ!Box-Einstellungen an (mit selbst gewähltem Kennwort) und legt die Datei in `config/fritzbox_manager_backups/` ab. Nur für Administratoren, zwei Schalter (Hauptschalter *Experimentelle Funktionen* und *Backup*), beide standardmäßig aus; das Kennwort wird weder gespeichert noch protokolliert. **Nicht an einer echten Box geprüft.** Details und Testschritte: [EXPERIMENTELL.md](EXPERIMENTELL.md).
- **Korrigiert: DSL-Werte „0“.** Liefert die Box keine DSL-Verbindung (z. B. Glasfaser-Modelle), zeigt die Karte „–“ mit Hinweis statt Nullwerten.
- **Besser erkennbar: leere WLAN-Liste.** Kann die Box die WLAN-Netze nicht liefern, nennt die Karte den Grund (z. B. fehlende Benutzerrechte) statt nur „keine WLAN-Netze“. Die eigentliche Ursache beim gemeldeten Fall ist **nicht bestätigt**; bitte Rechte „FRITZ!Box Einstellungen“ des Benutzers prüfen.
- Neu: Service `fritzbox_manager.create_backup`, Ereignis `fritzbox_manager_backup_created`, Optionen *Experimentelle Funktionen*, *Backup*, *Anzahl aufbewahrter Backups*.

## Bilder

Alle Bilder zeigen **Version 0.0.1b0 mit Testdaten** (keine echte FRITZ!Box); sie wurden für 0.0.2b1 noch nicht neu erstellt, der neue Bereich *Experimentell* ist darauf nicht zu sehen.

| Übersicht | WLAN | WLAN-Popup |
|:-:|:-:|:-:|
| ![Übersicht (Testdaten)](docs/images/uebersicht.webp) | ![WLAN-Liste (Testdaten)](docs/images/wlan.webp) | ![WLAN-Popup (Testdaten)](docs/images/wlan-popup.webp) |

| Modul-Popup | Einstellungen |
|:-:|:-:|
| ![Modul-Popup mit Platzhalterkarte (Testdaten)](docs/images/modul-popup.webp) | ![Einstellungen (Testdaten)](docs/images/einstellungen.webp) |

Im Modul-Popup siehst du hier eine Platzhalterkarte; im Betrieb erscheint dort die Karte deiner Schwester-Integration.

## Voraussetzungen

- Home Assistant 2025.6 oder neuer.
- FRITZ!Box mit aktivierter TR-064-Schnittstelle („Zugriff für Anwendungen zulassen“ unter Heimnetz → Netzwerk → Netzwerkeinstellungen) und einem Benutzer mit den Rechten **FRITZ!Box Einstellungen** (und für Neustart/WLAN-Schalten entsprechende Rechte).
- Für die Popups: die Integrationen [FRITZ!Box Anrufe](https://github.com/Meine-smarte-Welt/fritzbox_anrufe), [FRITZ!Box Netzwerk](https://github.com/Meine-smarte-Welt/fritzbox_netzwerk) und [FRITZ!Box Ereignisse](https://github.com/Meine-smarte-Welt/fritzbox_ereignisse) (jeweils optional).

## Installation

**HACS:** Benutzerdefiniertes Repository `https://github.com/Meine-smarte-Welt/fritzbox_manager` (Kategorie *Integration*) hinzufügen. Da es sich um ein Pre-release handelt, muss in HACS bei diesem Repository **„Beta-Versionen anzeigen“** aktiviert sein. Herunterladen, Home Assistant neu starten.

**Manuell:** Ordner `custom_components/fritzbox_manager` nach `config/custom_components/` kopieren, neu starten.

Die Karte wird automatisch als Lovelace-Ressource (`/fritzbox_manager_files/fritzbox-manager-card.js`) eingetragen. Im YAML-Modus trägst du sie selbst ein (Typ *module*). Danach Browser neu laden (Strg+F5).

## Einrichtung

*Einstellungen → Geräte & Dienste → Integration hinzufügen → FRITZ!Box Manager.* Host (meist `fritz.box`), Benutzername, Passwort, optional HTTPS. Über „Neu konfigurieren“ änderst du die Zugangsdaten, über „Konfigurieren“ die Optionen.

## Die Karte

```yaml
type: custom:fritzbox-manager-card
```

Wichtige Schlüssel: `title`, `show_title`, `show_overview|system|internet|wifi|modules|settings`, `show_experimental`, `default_tab`, `zoom`, `read_only`, `entry_id` (nur bei mehreren Boxen), `module_calls_config`, `module_network_config`, `module_events_config`, `color_*`. Alles ist auch im grafischen Editor einstellbar. Beispiele: [`examples/`](examples/).

> Abweichung von den anderen Managern: Diese Karte hat keine Spaltenlisten und deshalb **keine** Suche, Filter, Sortierung oder Spaltenschalter.

## Farben

Leer = Theme-Standard. Erlaubt sind Hex, `rgb()`, `hsl()`, `var(--…)`; Ungültiges wird verworfen.

| Schlüssel | Bedeutung |
|---|---|
| `color_tab_active` | aktiver Tab |
| `color_success` / `color_warning` / `color_error` / `color_info` | Statusfarben |
| `color_row_icon` | Zeilensymbole |
| `color_live_banner` | Banner |
| `color_icon_<tab>` | Symbolfarbe je Kategorie |

## Services

| Service | Wirkung |
|---|---|
| `fritzbox_manager.set_wlan` | WLAN-Netz (`wlan1`…`wlan9`) ein-/ausschalten |
| `fritzbox_manager.reconnect` | Internetverbindung neu aufbauen |
| `fritzbox_manager.reboot` | Box neu starten |
| `fritzbox_manager.check_for_update` | App-Version bei GitHub prüfen |
| `fritzbox_manager.create_backup` | *Experimentell:* Backup der Box-Einstellungen erstellen (`password` erforderlich; nur mit aktivierten Schaltern) |

Alle Services sind Administratoren vorbehalten; `entry_id` ist optional.

## Ereignisse

`fritzbox_manager_internet_offline`, `fritzbox_manager_internet_online`, `fritzbox_manager_ip_changed` (mit `ip`, `previous_ip`), `fritzbox_manager_update_available` (mit `version`), `fritzbox_manager_backup_created` (mit `filename`, `size`; nur mit aktiviertem Backup). Alle tragen `entry_id`. Abschaltbar; beim Start wird nur der Ausgangszustand gemerkt (keine Ereignisflut). Beispiele: [`examples/`](examples/).

## Sensoren

Firmware, Laufzeit der Box und der Verbindung, externe IPv4/IPv6, IPv6-Präfix, Download-/Upload-Rate, maximale Leitungsraten, empfangene/gesendete Daten, letzter Verbindungsfehler, WLAN-Geräte, bekannte Netzwerkgeräte, DSL-Störabstand und -Dämpfung (nur wenn die Box Werte liefert), CPU-Temperatur (nur mit aktivierter Option). Binärsensoren: Internet, Leitung, Firmware-Update. Schalter: je WLAN-Netz. Schaltflächen: Neustart, Neu verbinden.

## Versionsanzeige und Update-Hinweis

Die Version steht an drei Stellen: Karte → Zahnrad → *App-Version*, oben im Karten-Editor und im Optionen-Dialog. Alle 12 Stunden wird GitHub nach einer neueren Version gefragt (auch Pre-releases, solange eine Beta läuft). Ist GitHub nicht erreichbar, läuft alles normal weiter.

## Einstellungen

Abfrageintervall (10–600 s, Standard 30 s), Ereignisse senden, CPU-Temperatur (experimentell, aus), Experimentelle Funktionen (Hauptschalter, aus), Backup (experimentell, aus), Anzahl aufbewahrter Backups (1–50, Standard 10). Der Bereich *Experimentell* erscheint in der Karte nur mit `show_experimental: true`.

## Sicherheit

- Schreibende Aktionen (WLAN schalten, Neustart, Neu verbinden, Backup, Optionen) nur für Administratoren, im Backend geprüft.
- Riskante Aktionen mit Zwei-Klick-Bestätigung.
- Alle Texte in der Karte werden maskiert, Farbwerte nur über eine Allowlist übernommen.
- Host und HTTPS-Angabe werden nur Administratoren übermittelt; die Diagnose anonymisiert Zugangsdaten und Adressen.
- `read_only` blendet alle Bedienelemente aus.

## Bekannte Einschränkungen

- **Nicht an echter Hardware getestet.** Getestet wurde gegen eine simulierte TR-064-Schnittstelle (Backend) und mit Testdaten im Browser (Karte). Dienste, Werte und Einheiten einer echten FRITZ!Box sind **ungeprüft**; je nach Modell/FRITZ!OS können Werte fehlen.
- **Gast-WLAN und Frequenzband sind Heuristiken:** Nutzt die Box keine passenden Angaben, gilt bei mindestens drei Netzen das letzte als Gast-Netz, das Band wird aus dem Kanal abgeleitet (6 GHz wird nicht unterschieden).
- **Keine CPU-/RAM-Auslastung.** Nur die CPU-Temperatur, experimentell, über eine nicht öffentlich dokumentierte Schnittstelle (standardmäßig aus).
- **Nur teilweise übersetzt geprüft:** Englisch und Niederländisch sind nicht von Muttersprachlern geprüft.
- Die Popups brauchen die jeweilige Schwester-Integration samt Karte; ohne sie zeigt die Karte eine Anleitung statt der Funktion.
- **Backup ist ungeprüft:** Ob die Box die Sicherung über TR-064 ausliefert, hängt von Modell, FRITZ!OS, Benutzerrechten und ggf. Zwei-Faktor-Bestätigung ab; es kann mit einem Fehlertext enden. Das Kennwort wird nicht gespeichert – ohne es lässt sich die Datei nicht an der Box einspielen. Das Dateiformat wird nicht geprüft (nur Größe und Typ). Das Einspielen geschieht bewusst nur an der Box selbst (*System → Sicherung*).
- **Glasfaser-Modelle haben keine DSL-Werte** (z. B. FRITZ!Box 5690 Pro): Dort bleiben die DSL-Felder leer.
- Notification Center (`#nc`) ist nicht angebunden.
- Pre-release: HACS zeigt sie nur mit „Beta-Versionen anzeigen“.

## Fehlerbehebung

- *Karte nicht gefunden:* Seite mit Strg+F5 neu laden; im YAML-Modus die Ressource von Hand eintragen.
- *Anmeldung schlägt fehl:* TR-064 und Benutzerrechte an der Box prüfen.
- *Popup zeigt „nicht gefunden“:* Schwester-Integration installieren oder Entitäten über `module_*_config` angeben.
- Fehler bitte mit Diagnose-Download unter [Issues](https://github.com/Meine-smarte-Welt/fritzbox_manager/issues) melden.

## Versionshistorie

| Version | Änderungen |
|---|---|
| **0.0.2b1** | Experimentell: Backup der Box-Einstellungen (Service, Karte, Ereignis). DSL-Nullwerte bei Modellen ohne DSL werden als „–“ angezeigt. Grund bei leerer WLAN-Liste wird angezeigt. |
| **0.0.1b0** | Erste Veröffentlichung (Beta): Integration, Karte mit 6 Kategorien, Module-Popups, WLAN-Schalten, Versionsanzeige. |

## Datei-Integrität

Die `.py`-, `.js`- und `.yaml`-Dateien tragen den SHA256-Hash ab Zeile 2 in der ersten Zeile (`tail -n +2 datei | sha256sum`). Für JSON-Dateien:

| Datei | SHA256 |
|---|---|
| `custom_components/fritzbox_manager/manifest.json` | `918064437ac1fb636b047a4648260b195759b016aab65f9d941bb2bd89aba937` |
| `custom_components/fritzbox_manager/strings.json` | `0d86ec24f652e4db9d9df83aa7006bd0af0b84d4ee667a6318aaabdb50021e4b` |
| `custom_components/fritzbox_manager/icons.json` | `b8b33129c6a6251f46d807f220e325b85d5923ec945e91a33b77a1f2f529ce0e` |
| `custom_components/fritzbox_manager/translations/de.json` | `0d86ec24f652e4db9d9df83aa7006bd0af0b84d4ee667a6318aaabdb50021e4b` |
| `custom_components/fritzbox_manager/translations/en.json` | `ceaf72b1ea6eb5f076248f7130846f53e3a74be7f75e48aeefdef061f13ede76` |
| `custom_components/fritzbox_manager/translations/nl.json` | `4f449f35bcc4c4e822f2282b7316e200456a004af1cbe11025e09f1002c8f7ff` |
| `hacs.json` | `360a813ce8c9ed6a42abd57d21c4b416646ffe3fe6777d8fd89145e9ef989a71` |

## Lizenz

MIT, siehe [LICENSE](LICENSE).
