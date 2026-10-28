// SHA256 (Inhalt ab Zeile 2, d.h. dieser Datei ohne diese erste Zeile): eaf83dc4f00f97605dd10f8348285168b6afb3ce36a3379a6393e1d3b2c4b270
/**
 * FRITZ!Box Manager Card
 *
 * Eine Karte für die Integration "fritzbox_manager": Übersicht, Box, Internet,
 * WLAN, Module (die Karten FRITZ!Box Anrufe / Netzwerk / Ereignisse als
 * Popup) und Einstellungen. Wird mit der Integration ausgeliefert und als
 * Lovelace-Ressource eingetragen.
 *
 * Aufbau nach dem Design-Master von "Meine smarte Welt".
 */

const CARD_VERSION = "0.0.1b0";
const DOMAIN = "fritzbox_manager";
const WS_SUBSCRIBE = "fritzbox_manager/subscribe";
const WS_ACTION = "fritzbox_manager/action";
const GITHUB_RELEASES = "https://github.com/Meine-smarte-Welt/fritzbox_manager/releases";
const GITHUB_REPO = "https://github.com/Meine-smarte-Welt/fritzbox_manager";

// --- Kategorien (Tabs) - an EINER Stelle gepflegt -------------------------------
const TAB_ORDER = ["overview", "system", "internet", "wifi", "modules", "settings"];
const TAB_META = {
  overview: { icon: "mdi:view-dashboard", label: "tab_overview" },
  system: { icon: "mdi:router-network", label: "tab_system" },
  internet: { icon: "mdi:web", label: "tab_internet" },
  wifi: { icon: "mdi:wifi", label: "tab_wifi" },
  modules: { icon: "mdi:puzzle", label: "tab_modules" },
  settings: { icon: "mdi:cog", label: "tab_settings" },
};
const CATEGORY_ICON_COLOR_KEYS = Object.fromEntries(TAB_ORDER.map((k) => [k, `color_icon_${k}`]));

// --- Module: die Schwester-Integrationen, die als Popup eingebunden werden -------
// detect() sucht die Entitäten über die Entitätsregistrierung (Plattform +
// translation_key) und notfalls über Attribute. Alles lässt sich per
// module_<name>_config in der Karte überschreiben.
const MODULE_ORDER = ["calls", "network", "events"];
const MODULES = {
  calls: {
    icon: "mdi:phone",
    domain: "fritzbox_anrufe",
    tag: "fritzbox-anrufe-card",
    repo: "https://github.com/Meine-smarte-Welt/fritzbox_anrufe",
    label: "mod_calls",
    desc: "mod_calls_desc",
    keys: { entity_eingehend: "fritzbox_anrufe_eingehend", entity_ausgehend: "fritzbox_anrufe_ausgehend", entity_verpasst: "fritzbox_anrufe_verpasst" },
  },
  network: {
    icon: "mdi:lan",
    domain: "fritzbox_netzwerk",
    tag: "fritzbox-netzwerk-card",
    repo: "https://github.com/Meine-smarte-Welt/fritzbox_netzwerk",
    label: "mod_network",
    desc: "mod_network_desc",
    keys: { entity: "geraete" },
  },
  events: {
    icon: "mdi:format-list-bulleted",
    domain: "fritzbox_ereignisse",
    tag: "fritzbox-ereignisse-card",
    repo: "https://github.com/Meine-smarte-Welt/fritzbox_ereignisse",
    label: "mod_events",
    desc: "mod_events_desc",
    keys: { entity: "fritzbox_ereignisse_ereignisse" },
  },
};

// --- Farben ---------------------------------------------------------------------
const COLOR_CONFIG_KEYS = {
  tab_active: { cssVar: "--fbm-color-tab-active", fallback: "var(--primary-color, #03a9f4)" },
  success: { cssVar: "--fbm-color-success", fallback: "var(--success-color, #43a047)" },
  warning: { cssVar: "--fbm-color-warning", fallback: "var(--warning-color, #ff9800)" },
  error: { cssVar: "--fbm-color-error", fallback: "var(--error-color, #db4437)" },
  info: { cssVar: "--fbm-color-info", fallback: "var(--info-color, #039be5)" },
  row_icon: { cssVar: "--fbm-color-row-icon", fallback: "var(--secondary-text-color, #727272)" },
  live_banner: { cssVar: "--fbm-color-live-banner", fallback: "var(--state-icon-active-color, #03a9f4)" },
};
// verwirft ; { } < > Anführungszeichen
const SAFE_COLOR_RE = /^[a-zA-Z0-9#(),.%\-\s]+$/;
function sanitizeColor(v) {
  const t = String(v || "").trim();
  return t && SAFE_COLOR_RE.test(t) ? t : "";
}

const CONFIG_DEFAULTS = {
  title: undefined,
  show_title: true,
  entry_id: "",
  show_overview: true,
  show_system: true,
  show_internet: true,
  show_wifi: true,
  show_modules: true,
  show_settings: true,
  default_tab: "overview",
  max_rows: 20,
  zoom: 1,
  show_stats: true,
  read_only: false,
  show_module_calls: true,
  show_module_network: true,
  show_module_events: true,
  module_calls_config: {},
  module_network_config: {},
  module_events_config: {},
};

// --- Sprachen -------------------------------------------------------------------
// Projektsprachen: de, en, nl. Fehlt ein Schlüssel, greift Englisch, dann der Schlüsselname.
const I18N = {
  de: {
    default_title: "FRITZ!Box Manager",
    tab_overview: "Übersicht", tab_system: "Box", tab_internet: "Internet", tab_wifi: "WLAN", tab_modules: "Module", tab_settings: "Einstellungen",
    loading: "Warte auf Daten der FRITZ!Box …",
    not_found: "Keine eingerichtete FRITZ!Box Manager-Integration gefunden. Prüfe unter Einstellungen > Geräte & Dienste.",
    conn_lost: "Keine Verbindung zur FRITZ!Box. Die letzten bekannten Werte werden angezeigt.",
    reboot_running: "Neustart läuft … die FRITZ!Box ist in wenigen Minuten wieder erreichbar.",
    card_mismatch: "Karte ({card}) und Integration ({integration}) haben verschiedene Versionen. Leere den Browser-Cache (Strg+F5).",
    app_update_banner: "Neue Version {v} verfügbar. Aktualisiere über HACS.",
    chip_online: "Internet verbunden", chip_offline: "Internet getrennt", chip_unknown: "Internet unbekannt",
    chip_clients: "{n} WLAN-Geräte", chip_fw_update: "Firmware-Update", chip_fw_ok: "Firmware aktuell",
    t_internet: "Internet", t_download: "Download", t_upload: "Upload", t_wifi: "WLAN", t_box: "FRITZ!Box", t_traffic: "Datenmenge", t_dsl: "DSL-Leitung", t_quick: "Schnellzugriff",
    l_ipv4: "IPv4-Adresse", l_ipv6: "IPv6-Adresse", l_prefix: "IPv6-Präfix", l_conn_uptime: "Verbunden seit", l_uptime: "Laufzeit der Box", l_model: "Modell", l_firmware: "Firmware", l_hardware: "Hardware",
    l_max: "Maximal", l_received: "Empfangen", l_sent: "Gesendet", l_status: "Status", l_last_error: "Letzter Fehler", l_link: "Leitung", l_access: "Zugangsart",
    l_noise_down: "Störabstand Download", l_noise_up: "Störabstand Upload", l_atten_down: "Dämpfung Download", l_atten_up: "Dämpfung Upload",
    l_networks: "Aktive Netze", l_clients: "WLAN-Geräte", l_known: "Bekannte Geräte im Heimnetz", l_cpu: "CPU-Temperatur", l_new_version: "Neue Firmware", l_current: "Aktuell", l_rate_down: "Download aktuell", l_rate_up: "Upload aktuell",
    a_info: "Informationen", a_firmware: "Firmware", a_conn: "Verbindung", a_addresses: "Adressen", a_speed: "Geschwindigkeit", a_traffic: "Datenmenge", a_dsl: "DSL-Werte", a_temp: "Temperatur",
    a_app: "App-Version", a_box_conn: "Verbindung zur FRITZ!Box", a_options: "Optionen", a_maintenance: "Wartung", a_events: "Ereignisse seit dem Start", a_switch: "Schalten", a_diag: "Diagnose",
    v_integration: "Integration", v_card: "Karte", v_latest: "Neueste Version", v_checked: "Zuletzt geprüft", v_check_now: "Jetzt prüfen", v_release: "Release ansehen",
    v_up_to_date: "Aktuell", v_update: "Update verfügbar", v_failed: "Prüfung nicht möglich", v_never: "noch nicht",
    v_hint: "Aktualisiere über HACS und starte Home Assistant neu. Danach Browser neu laden (Strg+F5).",
    v_beta_hint: "Dies ist eine Beta-Version. In HACS müssen „Beta-Versionen anzeigen“ aktiv sein, um Beta-Updates zu sehen.",
    c_host: "Adresse", c_state: "Zustand", c_connected: "verbunden", c_disconnected: "nicht erreichbar", c_updated: "Letzte Abfrage", c_interval: "Abfrageintervall", c_secure: "Verschlüsselt (HTTPS)", c_yes: "ja", c_no: "nein",
    o_scan: "Abfrageintervall (Sekunden)", o_events: "Home-Assistant-Ereignisse senden", o_events_hint: "Internet getrennt/verbunden, neue IP-Adresse, Firmware-Update.", o_cpu: "CPU-Temperatur abfragen (experimentell)", o_cpu_hint: "Nutzt eine nicht öffentlich dokumentierte Schnittstelle der Box.", o_saved: "Gespeichert", o_readonly: "Nur Ansicht – Änderungen sind in dieser Karte gesperrt.", o_admin: "Änderungen sind Administratoren vorbehalten.",
    m_reboot: "FRITZ!Box neu starten", m_reboot_hint: "Unterbricht das Internet und alle Netze für einige Minuten.", m_reconnect: "Internetverbindung neu aufbauen", m_reconnect_hint: "Trennt die Verbindung kurz und baut sie neu auf, meist mit neuer IP-Adresse.", m_confirm: "Wirklich?", m_sent: "Auftrag gesendet",
    ev_internet_offline: "Internet getrennt", ev_internet_online: "Internet wieder verbunden", ev_ip_changed: "Neue IP-Adresse", ev_firmware_update: "Firmware-Update verfügbar: {version}", ev_connection_lost: "Verbindung zur FRITZ!Box verloren", ev_connection_restored: "Verbindung zur FRITZ!Box wiederhergestellt",
    ev_wlan_changed_on: "WLAN „{wlan}“ eingeschaltet", ev_wlan_changed_off: "WLAN „{wlan}“ ausgeschaltet", ev_option_changed: "Option geändert: {option}", ev_reboot_requested: "Neustart angefordert", ev_reconnect_requested: "Neuverbindung angefordert",
    ev_empty: "Seit dem Start gab es keine Ereignisse.", ev_clear: "Protokoll leeren", ev_more: "{n} weitere nicht angezeigt",
    w_guest: "Gast", w_band: "Frequenz", w_channel: "Kanal", w_standard: "Standard", w_clients: "Geräte", w_status: "Status", w_on: "an", w_off: "aus", w_turn_on: "Einschalten", w_turn_off: "Ausschalten", w_empty: "Die FRITZ!Box hat keine WLAN-Netze gemeldet.", w_type: "Art", w_normal: "Normal", w_guest_net: "Gastnetz", w_guest_hint: "Gastnetz erkannt nach der Angabe der Box oder, falls diese fehlt, anhand der Nummer (Schätzung).", w_off_warn: "Schaltest du das WLAN aus, über das du gerade verbunden bist, verlierst du die Verbindung.",
    mod_calls: "Anrufe", mod_network: "Netzwerk", mod_events: "Ereignisse",
    mod_calls_desc: "Anrufliste, Anrufbeantworter, Live-Anzeige", mod_network_desc: "Alle Geräte im Heimnetz", mod_events_desc: "Ereignisprotokoll der FRITZ!Box",
    mod_ready: "bereit", mod_missing: "nicht installiert", mod_noentity: "Entitäten nicht gefunden", mod_open: "Öffnen", mod_repo: "Auf GitHub ansehen",
    mod_missing_text: "Die Karte „{name}“ ist in diesem Browser nicht geladen. Installiere die Integration über HACS und lade die Seite neu (Strg+F5).",
    mod_noentity_text: "Die Sensoren von „{name}“ wurden nicht automatisch gefunden. Trage sie in der Karten-Konfiguration unter „{key}“ ein.",
    mod_error_text: "Die Karte „{name}“ konnte nicht angezeigt werden.",
    b_close: "Schließen", b_copy: "Kopieren", b_copied: "Kopiert", na: "—", unit_d: "d", unit_h: "h", unit_min: "min",
    banner_error: "Fehler", more_info: "Mehr Info",
  },
  en: {
    default_title: "FRITZ!Box Manager",
    tab_overview: "Overview", tab_system: "Box", tab_internet: "Internet", tab_wifi: "Wi-Fi", tab_modules: "Modules", tab_settings: "Settings",
    loading: "Waiting for data from the FRITZ!Box …",
    not_found: "No configured FRITZ!Box Manager integration found. Check Settings > Devices & services.",
    conn_lost: "No connection to the FRITZ!Box. The last known values are shown.",
    reboot_running: "Restart in progress … the FRITZ!Box will be back in a few minutes.",
    card_mismatch: "Card ({card}) and integration ({integration}) have different versions. Clear the browser cache (Ctrl+F5).",
    app_update_banner: "New version {v} available. Update via HACS.",
    chip_online: "Internet connected", chip_offline: "Internet down", chip_unknown: "Internet unknown",
    chip_clients: "{n} Wi-Fi devices", chip_fw_update: "Firmware update", chip_fw_ok: "Firmware up to date",
    t_internet: "Internet", t_download: "Download", t_upload: "Upload", t_wifi: "Wi-Fi", t_box: "FRITZ!Box", t_traffic: "Data volume", t_dsl: "DSL line", t_quick: "Quick access",
    l_ipv4: "IPv4 address", l_ipv6: "IPv6 address", l_prefix: "IPv6 prefix", l_conn_uptime: "Connected for", l_uptime: "Box uptime", l_model: "Model", l_firmware: "Firmware", l_hardware: "Hardware",
    l_max: "Maximum", l_received: "Received", l_sent: "Sent", l_status: "Status", l_last_error: "Last error", l_link: "Line", l_access: "Access type",
    l_noise_down: "Noise margin download", l_noise_up: "Noise margin upload", l_atten_down: "Attenuation download", l_atten_up: "Attenuation upload",
    l_networks: "Active networks", l_clients: "Wi-Fi devices", l_known: "Known devices in the home network", l_cpu: "CPU temperature", l_new_version: "New firmware", l_current: "Current", l_rate_down: "Download now", l_rate_up: "Upload now",
    a_info: "Information", a_firmware: "Firmware", a_conn: "Connection", a_addresses: "Addresses", a_speed: "Speed", a_traffic: "Data volume", a_dsl: "DSL values", a_temp: "Temperature",
    a_app: "App version", a_box_conn: "Connection to the FRITZ!Box", a_options: "Options", a_maintenance: "Maintenance", a_events: "Events since start", a_switch: "Switch", a_diag: "Diagnostics",
    v_integration: "Integration", v_card: "Card", v_latest: "Latest version", v_checked: "Last checked", v_check_now: "Check now", v_release: "View release",
    v_up_to_date: "Up to date", v_update: "Update available", v_failed: "Check not possible", v_never: "not yet",
    v_hint: "Update via HACS and restart Home Assistant. Then reload the browser (Ctrl+F5).",
    v_beta_hint: "This is a beta version. In HACS, \"Show beta versions\" must be enabled to see beta updates.",
    c_host: "Address", c_state: "State", c_connected: "connected", c_disconnected: "unreachable", c_updated: "Last poll", c_interval: "Polling interval", c_secure: "Encrypted (HTTPS)", c_yes: "yes", c_no: "no",
    o_scan: "Polling interval (seconds)", o_events: "Send Home Assistant events", o_events_hint: "Internet down/up, new IP address, firmware update.", o_cpu: "Read CPU temperature (experimental)", o_cpu_hint: "Uses an undocumented interface of the box.", o_saved: "Saved", o_readonly: "View only – changes are locked in this card.", o_admin: "Changes are reserved for administrators.",
    m_reboot: "Restart FRITZ!Box", m_reboot_hint: "Interrupts the internet and all networks for a few minutes.", m_reconnect: "Re-establish internet connection", m_reconnect_hint: "Drops the connection briefly and re-establishes it, usually with a new IP address.", m_confirm: "Really?", m_sent: "Request sent",
    ev_internet_offline: "Internet down", ev_internet_online: "Internet connected again", ev_ip_changed: "New IP address", ev_firmware_update: "Firmware update available: {version}", ev_connection_lost: "Lost connection to the FRITZ!Box", ev_connection_restored: "Connection to the FRITZ!Box restored",
    ev_wlan_changed_on: "Wi-Fi \"{wlan}\" turned on", ev_wlan_changed_off: "Wi-Fi \"{wlan}\" turned off", ev_option_changed: "Option changed: {option}", ev_reboot_requested: "Restart requested", ev_reconnect_requested: "Reconnect requested",
    ev_empty: "No events since start.", ev_clear: "Clear log", ev_more: "{n} more not shown",
    w_guest: "Guest", w_band: "Band", w_channel: "Channel", w_standard: "Standard", w_clients: "Devices", w_status: "Status", w_on: "on", w_off: "off", w_turn_on: "Turn on", w_turn_off: "Turn off", w_empty: "The FRITZ!Box reported no Wi-Fi networks.", w_type: "Type", w_normal: "Normal", w_guest_net: "Guest network", w_guest_hint: "Guest network detected from the box's own information or, if missing, by its number (estimate).", w_off_warn: "If you turn off the Wi-Fi you are connected through, you will lose the connection.",
    mod_calls: "Calls", mod_network: "Network", mod_events: "Events",
    mod_calls_desc: "Call list, answering machine, live view", mod_network_desc: "All devices in the home network", mod_events_desc: "FRITZ!Box event log",
    mod_ready: "ready", mod_missing: "not installed", mod_noentity: "entities not found", mod_open: "Open", mod_repo: "View on GitHub",
    mod_missing_text: "The card \"{name}\" is not loaded in this browser. Install the integration via HACS and reload the page (Ctrl+F5).",
    mod_noentity_text: "The sensors of \"{name}\" were not found automatically. Enter them in the card configuration under \"{key}\".",
    mod_error_text: "The card \"{name}\" could not be displayed.",
    b_close: "Close", b_copy: "Copy", b_copied: "Copied", na: "—", unit_d: "d", unit_h: "h", unit_min: "min",
    banner_error: "Error", more_info: "More info",
  },
  nl: {
    default_title: "FRITZ!Box Manager",
    tab_overview: "Overzicht", tab_system: "Box", tab_internet: "Internet", tab_wifi: "Wifi", tab_modules: "Modules", tab_settings: "Instellingen",
    loading: "Wachten op gegevens van de FRITZ!Box …",
    not_found: "Geen ingestelde FRITZ!Box Manager-integratie gevonden. Controleer Instellingen > Apparaten en diensten.",
    conn_lost: "Geen verbinding met de FRITZ!Box. De laatst bekende waarden worden getoond.",
    reboot_running: "Herstart bezig … de FRITZ!Box is over enkele minuten weer bereikbaar.",
    card_mismatch: "Kaart ({card}) en integratie ({integration}) hebben verschillende versies. Wis de browsercache (Ctrl+F5).",
    app_update_banner: "Nieuwe versie {v} beschikbaar. Werk bij via HACS.",
    chip_online: "Internet verbonden", chip_offline: "Internet verbroken", chip_unknown: "Internet onbekend",
    chip_clients: "{n} wifi-apparaten", chip_fw_update: "Firmware-update", chip_fw_ok: "Firmware actueel",
    t_internet: "Internet", t_download: "Download", t_upload: "Upload", t_wifi: "Wifi", t_box: "FRITZ!Box", t_traffic: "Datavolume", t_dsl: "DSL-lijn", t_quick: "Snelle toegang",
    l_ipv4: "IPv4-adres", l_ipv6: "IPv6-adres", l_prefix: "IPv6-prefix", l_conn_uptime: "Verbonden sinds", l_uptime: "Looptijd van de box", l_model: "Model", l_firmware: "Firmware", l_hardware: "Hardware",
    l_max: "Maximaal", l_received: "Ontvangen", l_sent: "Verzonden", l_status: "Status", l_last_error: "Laatste fout", l_link: "Lijn", l_access: "Toegangstype",
    l_noise_down: "Ruismarge download", l_noise_up: "Ruismarge upload", l_atten_down: "Demping download", l_atten_up: "Demping upload",
    l_networks: "Actieve netwerken", l_clients: "Wifi-apparaten", l_known: "Bekende apparaten in het thuisnetwerk", l_cpu: "CPU-temperatuur", l_new_version: "Nieuwe firmware", l_current: "Actueel", l_rate_down: "Download nu", l_rate_up: "Upload nu",
    a_info: "Informatie", a_firmware: "Firmware", a_conn: "Verbinding", a_addresses: "Adressen", a_speed: "Snelheid", a_traffic: "Datavolume", a_dsl: "DSL-waarden", a_temp: "Temperatuur",
    a_app: "App-versie", a_box_conn: "Verbinding met de FRITZ!Box", a_options: "Opties", a_maintenance: "Onderhoud", a_events: "Gebeurtenissen sinds start", a_switch: "Schakelen", a_diag: "Diagnose",
    v_integration: "Integratie", v_card: "Kaart", v_latest: "Nieuwste versie", v_checked: "Laatst gecontroleerd", v_check_now: "Nu controleren", v_release: "Release bekijken",
    v_up_to_date: "Actueel", v_update: "Update beschikbaar", v_failed: "Controle niet mogelijk", v_never: "nog niet",
    v_hint: "Werk bij via HACS en start Home Assistant opnieuw. Laad daarna de browser opnieuw (Ctrl+F5).",
    v_beta_hint: "Dit is een bètaversie. In HACS moet \"Bètaversies tonen\" actief zijn om bèta-updates te zien.",
    c_host: "Adres", c_state: "Status", c_connected: "verbonden", c_disconnected: "onbereikbaar", c_updated: "Laatste opvraging", c_interval: "Ophaalinterval", c_secure: "Versleuteld (HTTPS)", c_yes: "ja", c_no: "nee",
    o_scan: "Ophaalinterval (seconden)", o_events: "Home Assistant-gebeurtenissen versturen", o_events_hint: "Internet weg/terug, nieuw IP-adres, firmware-update.", o_cpu: "CPU-temperatuur ophalen (experimenteel)", o_cpu_hint: "Gebruikt een niet openbaar gedocumenteerde interface van de box.", o_saved: "Opgeslagen", o_readonly: "Alleen weergave – wijzigingen zijn in deze kaart geblokkeerd.", o_admin: "Wijzigingen zijn voorbehouden aan beheerders.",
    m_reboot: "FRITZ!Box herstarten", m_reboot_hint: "Onderbreekt internet en alle netwerken voor enkele minuten.", m_reconnect: "Internetverbinding opnieuw opbouwen", m_reconnect_hint: "Verbreekt de verbinding kort en bouwt die opnieuw op, meestal met een nieuw IP-adres.", m_confirm: "Zeker?", m_sent: "Opdracht verzonden",
    ev_internet_offline: "Internet verbroken", ev_internet_online: "Internet weer verbonden", ev_ip_changed: "Nieuw IP-adres", ev_firmware_update: "Firmware-update beschikbaar: {version}", ev_connection_lost: "Verbinding met de FRITZ!Box verloren", ev_connection_restored: "Verbinding met de FRITZ!Box hersteld",
    ev_wlan_changed_on: "Wifi \"{wlan}\" ingeschakeld", ev_wlan_changed_off: "Wifi \"{wlan}\" uitgeschakeld", ev_option_changed: "Optie gewijzigd: {option}", ev_reboot_requested: "Herstart aangevraagd", ev_reconnect_requested: "Opnieuw verbinden aangevraagd",
    ev_empty: "Sinds de start waren er geen gebeurtenissen.", ev_clear: "Logboek wissen", ev_more: "{n} meer niet getoond",
    w_guest: "Gast", w_band: "Frequentie", w_channel: "Kanaal", w_standard: "Standaard", w_clients: "Apparaten", w_status: "Status", w_on: "aan", w_off: "uit", w_turn_on: "Inschakelen", w_turn_off: "Uitschakelen", w_empty: "De FRITZ!Box heeft geen wifi-netwerken gemeld.", w_type: "Soort", w_normal: "Normaal", w_guest_net: "Gastnetwerk", w_guest_hint: "Gastnetwerk herkend aan de informatie van de box of, als die ontbreekt, aan het nummer (schatting).", w_off_warn: "Schakel je het wifi uit waarmee je nu verbonden bent, dan verlies je de verbinding.",
    mod_calls: "Gesprekken", mod_network: "Netwerk", mod_events: "Gebeurtenissen",
    mod_calls_desc: "Gespreksgeschiedenis, antwoordapparaat, live-weergave", mod_network_desc: "Alle apparaten in het thuisnetwerk", mod_events_desc: "Gebeurtenissenlogboek van de FRITZ!Box",
    mod_ready: "gereed", mod_missing: "niet geïnstalleerd", mod_noentity: "entiteiten niet gevonden", mod_open: "Openen", mod_repo: "Bekijken op GitHub",
    mod_missing_text: "De kaart \"{name}\" is in deze browser niet geladen. Installeer de integratie via HACS en laad de pagina opnieuw (Ctrl+F5).",
    mod_noentity_text: "De sensoren van \"{name}\" zijn niet automatisch gevonden. Vul ze in bij de kaartconfiguratie onder \"{key}\".",
    mod_error_text: "De kaart \"{name}\" kon niet worden weergegeven.",
    b_close: "Sluiten", b_copy: "Kopiëren", b_copied: "Gekopieerd", na: "—", unit_d: "d", unit_h: "u", unit_min: "min",
    banner_error: "Fout", more_info: "Meer info",
  },
};

/** Sprach-Tag nie blind kürzen: erst exakter Treffer, dann Sprachteil, sonst Englisch. */
function normalizeLang(tag) {
  const t = String(tag || "en");
  if (I18N[t]) return t;
  const base = t.split("-")[0];
  return I18N[base] ? base : "en";
}
function translate(lang, key, params) {
  const l = normalizeLang(lang);
  let s = (I18N[l] && I18N[l][key]) || (I18N.en && I18N.en[key]) || key;
  if (params) for (const [k, v] of Object.entries(params)) s = s.split(`{${k}}`).join(String(v));
  return s;
}

// --- Hilfsfunktionen ------------------------------------------------------------
const ESC_MAP = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
/** Alle dynamischen Texte (SSIDs, Meldungen, Versionen) werden maskiert. */
function esc(value) {
  return String(value === null || value === undefined ? "" : value).replace(/[&<>"']/g, (c) => ESC_MAP[c]);
}

function numFmt(lang, value, digits) {
  try {
    return new Intl.NumberFormat(lang, { minimumFractionDigits: 0, maximumFractionDigits: digits }).format(value);
  } catch (e) {
    return String(Math.round(value * 10 ** digits) / 10 ** digits);
  }
}

/** Bit pro Sekunde → { num, unit } in passender Größe. */
function fmtRate(lang, bps) {
  if (bps === null || bps === undefined || Number.isNaN(Number(bps))) return null;
  const v = Number(bps);
  if (v >= 1e9) return { num: numFmt(lang, v / 1e9, 2), unit: "Gbit/s" };
  if (v >= 1e6) return { num: numFmt(lang, v / 1e6, v >= 1e8 ? 0 : 1), unit: "Mbit/s" };
  if (v >= 1e3) return { num: numFmt(lang, v / 1e3, 0), unit: "kbit/s" };
  return { num: numFmt(lang, v, 0), unit: "bit/s" };
}
function rateText(lang, bps, na) {
  const r = fmtRate(lang, bps);
  return r ? `${r.num} ${r.unit}` : na;
}

/** Byte → Text mit dezimalen Einheiten (wie bei der FRITZ!Box). */
function fmtBytes(lang, bytes, na) {
  if (bytes === null || bytes === undefined || Number.isNaN(Number(bytes))) return na;
  const v = Number(bytes);
  const units = ["B", "kB", "MB", "GB", "TB", "PB"];
  let i = 0;
  let x = v;
  while (x >= 1000 && i < units.length - 1) {
    x /= 1000;
    i += 1;
  }
  return `${numFmt(lang, x, i >= 3 ? 2 : i >= 1 ? 1 : 0)} ${units[i]}`;
}

function fmtDuration(seconds, t) {
  if (seconds === null || seconds === undefined || Number.isNaN(Number(seconds))) return t("na");
  let s = Math.max(0, Math.floor(Number(seconds)));
  const d = Math.floor(s / 86400);
  s -= d * 86400;
  const h = Math.floor(s / 3600);
  s -= h * 3600;
  const m = Math.floor(s / 60);
  if (d > 0) return `${d} ${t("unit_d")} ${h} ${t("unit_h")}`;
  if (h > 0) return `${h} ${t("unit_h")} ${m} ${t("unit_min")}`;
  return `${m} ${t("unit_min")}`;
}

function fmtDateTime(lang, iso, na) {
  if (!iso) return na;
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return na;
  try {
    return new Intl.DateTimeFormat(lang, { dateStyle: "short", timeStyle: "medium" }).format(d);
  } catch (e) {
    return d.toLocaleString();
  }
}

function fmtRelative(lang, iso, na) {
  if (!iso) return na;
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return na;
  const diff = Math.round((d.getTime() - Date.now()) / 1000);
  const abs = Math.abs(diff);
  let unit = "second";
  let value = diff;
  if (abs >= 86400) {
    unit = "day";
    value = Math.round(diff / 86400);
  } else if (abs >= 3600) {
    unit = "hour";
    value = Math.round(diff / 3600);
  } else if (abs >= 60) {
    unit = "minute";
    value = Math.round(diff / 60);
  }
  try {
    return new Intl.RelativeTimeFormat(lang, { numeric: "auto" }).format(value, unit);
  } catch (e) {
    return fmtDateTime(lang, iso, na);
  }
}

/** Kleine Verlaufslinie (SVG) aus einer Liste von Werten. */
function sparkline(values, cssVar) {
  const pts = (values || []).filter((v) => typeof v === "number");
  if (pts.length < 2) return '<svg class="spark" viewBox="0 0 100 28" preserveAspectRatio="none" aria-hidden="true"></svg>';
  const max = Math.max(...pts, 1);
  const step = 100 / (pts.length - 1);
  const line = pts.map((v, i) => `${(i * step).toFixed(2)},${(26 - (v / max) * 24).toFixed(2)}`).join(" ");
  const area = `0,27 ${line} 100,27`;
  return `<svg class="spark" viewBox="0 0 100 28" preserveAspectRatio="none" aria-hidden="true"><polygon points="${area}" style="fill:var(${cssVar});opacity:.15"/><polyline points="${line}" style="stroke:var(${cssVar})"/></svg>`;
}

/** Ersetzt Entitäts-Detektion der Schwesterkarten (siehe MODULES). */
function detectModuleEntities(hass, def) {
  const out = {};
  const entities = (hass && hass.entities) || {};
  const ids = Object.keys(entities).sort();
  for (const [key, translationKey] of Object.entries(def.keys)) {
    const id = ids.find((eid) => {
      const e = entities[eid];
      return e && e.platform === def.domain && e.translation_key === translationKey && !e.hidden;
    });
    if (id) out[key] = id;
  }
  // Rückfall für die Geräteliste: der Sammelsensor trägt das Attribut "hosts" (eine Liste).
  if (def.domain === "fritzbox_netzwerk" && !out.entity) {
    const states = (hass && hass.states) || {};
    const id = Object.keys(states)
      .sort()
      .find((eid) => eid.startsWith("sensor.") && Array.isArray(states[eid].attributes && states[eid].attributes.hosts));
    if (id) out.entity = id;
  }
  return out;
}

// --- Gestaltung -----------------------------------------------------------------
const STYLES = `
:host { display: block; }
ha-card { container-type: inline-size; container-name: fbm; overflow: hidden; }
* { box-sizing: border-box; }
.wrap { padding: 12px 16px 16px; }
.title { font-size: 1.25rem; font-weight: 500; padding: 4px 0 10px; color: var(--primary-text-color); }
button { font: inherit; color: inherit; }
.muted { color: var(--secondary-text-color); }
.grow { flex: 1 1 auto; min-width: 0; }
ha-icon { --mdc-icon-size: 22px; }

/* Banner */
.banner { display: flex; align-items: center; gap: 10px; padding: 10px 12px; margin: 0 0 12px; border-radius: 8px; border: 1px solid var(--c); background: color-mix(in srgb, var(--c) 12%, transparent); font-size: .92rem; }
.banner.error { --c: var(--fbm-color-error, var(--error-color, #db4437)); }
.banner.warning { --c: var(--fbm-color-warning, var(--warning-color, #ff9800)); }
.banner.live { --c: var(--fbm-color-live-banner, var(--state-icon-active-color, #03a9f4)); }
.banner ha-icon { color: var(--c); flex: none; }

/* Tabs */
.tabs { display: flex; gap: 4px; margin: 0 0 12px; border-bottom: 1px solid var(--divider-color); overflow-x: auto; scrollbar-width: none; }
.tab { position: relative; display: flex; align-items: center; justify-content: center; gap: 6px; flex: 1 1 0; min-width: 44px; padding: 10px 8px; background: none; border: 0; border-bottom: 3px solid transparent; cursor: pointer; color: var(--secondary-text-color); font-size: .92rem; white-space: nowrap; }
.tab:hover { background: color-mix(in srgb, var(--primary-text-color) 6%, transparent); }
.tab.active { color: var(--fbm-color-tab-active, var(--primary-color, #03a9f4)); border-bottom-color: var(--fbm-color-tab-active, var(--primary-color, #03a9f4)); }
.tab ha-icon { color: var(--ic, currentColor); }
.tab .badge { position: absolute; top: 4px; right: 4px; min-width: 16px; height: 16px; padding: 0 4px; border-radius: 8px; font-size: .68rem; line-height: 16px; text-align: center; color: #fff; background: var(--c); }
.badge.error { --c: var(--fbm-color-error, var(--error-color, #db4437)); }
.badge.warning { --c: var(--fbm-color-warning, var(--warning-color, #ff9800)); }
.badge.info { --c: var(--fbm-color-info, var(--info-color, #039be5)); }
@container fbm (max-width: 640px) { .tab:not(.active) .lbl { display: none; } .tab.active { flex: 2 1 0; } }
@container fbm (max-width: 480px) { .tab .lbl { display: none; } .tab.active { flex: 1 1 0; } }

/* Statistik-Chips */
.chips { display: flex; flex-wrap: wrap; gap: 8px; margin: 0 0 12px; }
.chip { display: inline-flex; align-items: center; gap: 6px; padding: 5px 10px; border-radius: 16px; border: 1px solid var(--c, var(--divider-color)); background: color-mix(in srgb, var(--c, transparent) 10%, transparent); font-size: .85rem; cursor: pointer; }
.chip ha-icon { --mdc-icon-size: 18px; color: var(--c, var(--secondary-text-color)); }
.chip.success, .pill.success, .dot.success { --c: var(--fbm-color-success, var(--success-color, #43a047)); }
.chip.warning, .pill.warning, .dot.warning { --c: var(--fbm-color-warning, var(--warning-color, #ff9800)); }
.chip.error, .pill.error, .dot.error { --c: var(--fbm-color-error, var(--error-color, #db4437)); }
.chip.info, .pill.info, .dot.info { --c: var(--fbm-color-info, var(--info-color, #039be5)); }

/* Kacheln */
.tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 10px; }
.tile { border: 1px solid var(--divider-color); border-radius: 10px; padding: 12px; min-width: 0; background: var(--card-background-color, transparent); }
.tile.wide { grid-column: 1 / -1; }
.tile h3 { margin: 0 0 8px; font-size: .8rem; font-weight: 500; text-transform: uppercase; letter-spacing: .04em; color: var(--secondary-text-color); display: flex; align-items: center; gap: 6px; }
.tile h3 ha-icon { --mdc-icon-size: 18px; color: var(--fbm-color-row-icon, var(--secondary-text-color)); }
.big { font-size: 1.7rem; font-weight: 500; line-height: 1.2; }
.big small { font-size: .85rem; font-weight: 400; color: var(--secondary-text-color); margin-left: 4px; }
.sub { font-size: .85rem; color: var(--secondary-text-color); margin-top: 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.spark { display: block; width: 100%; height: 34px; margin-top: 6px; }
.spark polyline { fill: none; stroke-width: 1.6; vector-effect: non-scaling-stroke; }
.kv { display: flex; justify-content: space-between; gap: 10px; padding: 3px 0; font-size: .9rem; }
.kv span:first-child { color: var(--secondary-text-color); }
.kv span:last-child { text-align: right; overflow-wrap: anywhere; }

.big.success { color: var(--fbm-color-success, var(--success-color, #43a047)); }
.big.error { color: var(--fbm-color-error, var(--error-color, #db4437)); }
.big.warning { color: var(--fbm-color-warning, var(--warning-color, #ff9800)); }
a.link { color: var(--primary-color, #03a9f4); text-decoration: none; }
a.link:hover { text-decoration: underline; }
.netlist { margin-top: 6px; display: flex; flex-direction: column; gap: 3px; font-size: .85rem; }
.netlist span { display: flex; align-items: center; gap: 6px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.netlist .dot { position: static; flex: none; border: 0; width: 8px; height: 8px; }

/* Pillen und Punkte */
.pill { display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px; border-radius: 10px; font-size: .78rem; border: 1px solid var(--c, var(--divider-color)); background: color-mix(in srgb, var(--c, transparent) 12%, transparent); white-space: nowrap; }
.dot { width: 9px; height: 9px; border-radius: 50%; background: var(--c, var(--disabled-text-color, #9e9e9e)); border: 2px solid var(--card-background-color, #fff); position: absolute; right: -2px; bottom: -2px; box-sizing: content-box; }

/* Zeilen */
.rows { border-top: 1px solid var(--divider-color); }
.row { display: flex; align-items: center; gap: 12px; padding: 10px 4px; border-bottom: 1px solid var(--divider-color); cursor: pointer; }
.row:hover { background: color-mix(in srgb, var(--primary-text-color) 5%, transparent); }
.row:focus-visible { outline: 2px solid var(--primary-color, #03a9f4); outline-offset: -2px; }
.ricon { position: relative; flex: none; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; border-radius: 50%; background: color-mix(in srgb, var(--fbm-color-row-icon, var(--secondary-text-color)) 12%, transparent); color: var(--ic, var(--fbm-color-row-icon, var(--secondary-text-color))); }
.rtitle { font-weight: 500; display: flex; align-items: center; gap: 6px; flex-wrap: wrap; overflow-wrap: anywhere; }
.rsub { font-size: .85rem; color: var(--secondary-text-color); }
.rend { display: flex; align-items: center; gap: 8px; flex: none; }

/* Knöpfe */
.btn { display: inline-flex; align-items: center; justify-content: center; gap: 6px; padding: 7px 12px; border-radius: 6px; border: 1px solid var(--divider-color); background: transparent; cursor: pointer; font-size: .9rem; }
.btn:hover { background: color-mix(in srgb, var(--primary-text-color) 7%, transparent); }
.btn.primary { background: var(--primary-color, #03a9f4); border-color: transparent; color: var(--text-primary-color, #fff); }
.btn.danger { border-color: var(--fbm-color-error, var(--error-color, #db4437)); color: var(--fbm-color-error, var(--error-color, #db4437)); }
.btn.danger.armed { background: var(--fbm-color-error, var(--error-color, #db4437)); color: #fff; }
.btn.small { padding: 3px 9px; font-size: .8rem; }
.btn.icon { padding: 6px; }
.btn[disabled] { opacity: .5; cursor: default; }
.actions { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }

/* Akkordeon */
.acc { border: 1px solid var(--divider-color); border-radius: 8px; margin: 0 0 8px; overflow: hidden; }
.acc.update { border-color: var(--fbm-color-warning, var(--warning-color, #ff9800)); }
.acc.danger { border-color: var(--fbm-color-error, var(--error-color, #db4437)); }
.acc > summary { list-style: none; display: flex; align-items: center; gap: 10px; padding: 10px 12px; cursor: pointer; font-weight: 500; }
.acc > summary::-webkit-details-marker { display: none; }
.acc > summary::after { content: ""; flex: none; width: 7px; height: 7px; border-right: 2px solid var(--secondary-text-color); border-bottom: 2px solid var(--secondary-text-color); transform: rotate(45deg); transition: transform .15s; margin: 0 4px 3px 4px; }
.acc[open] > summary::after { transform: rotate(-135deg); margin-bottom: -3px; }
.acc > summary ha-icon { color: var(--fbm-color-row-icon, var(--secondary-text-color)); }
.acc.update > summary ha-icon { color: var(--fbm-color-warning, var(--warning-color, #ff9800)); }
.acc.danger > summary ha-icon { color: var(--fbm-color-error, var(--error-color, #db4437)); }
.acc .meta { font-weight: 400; font-size: .85rem; color: var(--secondary-text-color); }
.acc-body { padding: 2px 12px 12px; }
.line { display: flex; justify-content: space-between; gap: 12px; padding: 5px 0; font-size: .92rem; border-bottom: 1px dashed color-mix(in srgb, var(--divider-color) 70%, transparent); }
.line:last-child { border-bottom: 0; }
.line .k { color: var(--secondary-text-color); }
.line .v { font-weight: 500; text-align: right; overflow-wrap: anywhere; }
.hint { font-size: .85rem; color: var(--secondary-text-color); margin: 6px 0 0; }
.hint.warn { color: var(--fbm-color-warning, var(--warning-color, #ff9800)); }
.field { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 6px 0; }
.field input[type=number] { width: 90px; padding: 6px 8px; border-radius: 6px; border: 1px solid var(--divider-color); background: var(--card-background-color, transparent); color: var(--primary-text-color); font: inherit; }
.field input[type=checkbox] { width: 20px; height: 20px; accent-color: var(--primary-color, #03a9f4); }
.ev { display: flex; align-items: flex-start; gap: 10px; padding: 6px 0; border-bottom: 1px solid var(--divider-color); font-size: .9rem; }
.ev .dot { position: static; margin-top: 5px; flex: none; }
.empty { padding: 18px 8px; text-align: center; color: var(--secondary-text-color); }

/* Popup */
.backdrop { position: fixed; inset: 0; z-index: 50; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,.5); padding: 12px; }
.popup { width: 100%; max-width: 440px; max-height: 86vh; display: flex; flex-direction: column; border-radius: 12px; background: var(--card-background-color, #fff); color: var(--primary-text-color); box-shadow: 0 10px 40px rgba(0,0,0,.4); overflow: hidden; }
.popup.wide { max-width: min(780px, 96vw); }
.phead { display: flex; align-items: center; gap: 10px; padding: 12px 14px; border-bottom: 1px solid var(--divider-color); }
.phead .ptitle { flex: 1 1 auto; font-weight: 500; font-size: 1.05rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.pbody { padding: 12px 14px 16px; overflow: auto; }
.pbody.module { padding: 0; }
.pbody.module > * { display: block; }
.helpbox { padding: 16px; }
.code { font-family: var(--code-font-family, monospace); font-size: .8rem; background: color-mix(in srgb, var(--primary-text-color) 7%, transparent); padding: 8px 10px; border-radius: 6px; white-space: pre-wrap; margin: 8px 0; }

/* Toast */
.toast { position: fixed; left: 50%; bottom: 24px; transform: translateX(-50%); z-index: 60; max-width: 90vw; padding: 10px 16px; border-radius: 8px; background: var(--primary-text-color, #222); color: var(--card-background-color, #fff); font-size: .9rem; box-shadow: 0 4px 16px rgba(0,0,0,.35); }
.toast.error { background: var(--fbm-color-error, var(--error-color, #db4437)); color: #fff; }
`;

// --- Die Karte ------------------------------------------------------------------
const EVENT_SEVERITY = {
  internet_offline: "error", connection_lost: "error",
  internet_online: "success", connection_restored: "success",
  ip_changed: "info", firmware_update: "info", wlan_changed: "info", option_changed: "info",
  reboot_requested: "warning", reconnect_requested: "warning",
};
const TOAST_MS = 5000;
const CONFIRM_MS = 5000;
const HISTORY_POINTS = 40;

function visibleTabs(cfg) {
  const tabs = TAB_ORDER.filter((k) => cfg[`show_${k}`] !== false);
  return tabs.length ? tabs : ["overview"];
}

class FritzboxManagerCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = null;
    this._hass = null;
    this._snap = null;
    this._error = null;
    this._unsub = null;
    this._subKey = null;
    this._subToken = 0;
    this._tabs = ["overview"];
    this._tab = "overview";
    this._open = {};
    this._confirm = null;
    this._confirmTimer = null;
    this._popup = null;
    this._modBody = null;
    this._modEl = null;
    this._initialised = false;
    this._iconColors = {};
    this._rowIconOverride = "";
    this._hassKey = "";
    this._busy = new Set();
    this._hist = { down: [], up: [] };
    this._lastFetched = null;
    this._sig = "";
    this._popupSig = "";
    this._toastTimer = null;
    this._onKey = (e) => {
      if (e.key === "Escape" && this._popup) this._closePopup();
    };
    this.shadowRoot.innerHTML =
      `<style>${STYLES}</style><ha-card><div class="wrap" id="main"></div></ha-card><div id="popup"></div><div id="toast"></div>`;
    const root = this.shadowRoot;
    root.addEventListener("click", (e) => this._onClick(e));
    root.addEventListener("keydown", (e) => this._onKeydown(e));
    root.addEventListener("change", (e) => this._onChange(e));
    // "toggle" bubbelt nicht - deshalb in der Capture-Phase. Kein Neuzeichnen hier (Endlosschleife).
    root.addEventListener(
      "toggle",
      (e) => {
        const el = e.target;
        if (el && el.matches && el.matches("details[data-k]")) this._open[el.dataset.k] = el.open;
      },
      true
    );
  }

  // --- Lebenszyklus ---
  connectedCallback() {
    window.addEventListener("keydown", this._onKey);
    if (this._hass && this._config) this._subscribe();
  }

  disconnectedCallback() {
    window.removeEventListener("keydown", this._onKey);
    this._unsubscribe();
    clearTimeout(this._confirmTimer);
    clearTimeout(this._toastTimer);
  }

  setConfig(config) {
    if (!config) throw new Error("fritzbox-manager-card: Konfiguration fehlt.");
    this._config = { ...CONFIG_DEFAULTS, ...config };
    this._tabs = visibleTabs(this._config);
    if (!this._tabs.includes(this._tab) || !this._initialised) {
      this._tab = this._tabs.includes(this._config.default_tab) ? this._config.default_tab : this._tabs[0];
    }
    this._initialised = true;
    this._applyColors();
    this._sig = "";
    if (this._hass) this._subscribe();
    this._render();
  }

  set hass(hass) {
    const first = !this._hass;
    this._hass = hass;
    if (!this._config) return;
    if (first || !this._unsub) this._subscribe();
    if (this._modEl) this._modEl.hass = hass;
    // Home Assistant setzt hass bei JEDER Zustandsänderung neu. Neu zeichnen nur, wenn
    // sich etwas ändert, das die Karte anzeigt: Sprache, Admin-Recht, Entitätsregister.
    const key = `${hass.language}|${hass.user && hass.user.is_admin}`;
    if (key !== this._hassKey || hass.entities !== this._hassEntities) {
      this._hassKey = key;
      this._hassEntities = hass.entities;
      this._render();
    }
  }

  get hass() {
    return this._hass;
  }

  getCardSize() {
    return 6;
  }

  static getConfigElement() {
    return document.createElement("fritzbox-manager-card-editor");
  }

  static getStubConfig() {
    return { type: "custom:fritzbox-manager-card" };
  }

  // --- Hilfen ---
  _lang() {
    return normalizeLang(this._hass && this._hass.language);
  }

  _t(key, params) {
    return translate(this._lang(), key, params);
  }

  _canEdit() {
    return !this._config.read_only && !!(this._hass && this._hass.user && this._hass.user.is_admin);
  }

  _data() {
    return (this._snap && this._snap.data) || {};
  }

  _applyColors() {
    const host = this.style;
    for (const [key, meta] of Object.entries(COLOR_CONFIG_KEYS)) {
      const value = sanitizeColor(this._config[`color_${key}`]);
      if (value) host.setProperty(meta.cssVar, value);
      else host.removeProperty(meta.cssVar);
    }
    this._iconColors = {};
    for (const tab of TAB_ORDER) this._iconColors[tab] = sanitizeColor(this._config[CATEGORY_ICON_COLOR_KEYS[tab]]);
    this._rowIconOverride = sanitizeColor(this._config.color_row_icon);
  }

  // --- Abo auf die Integration ---
  async _subscribe() {
    if (!this._hass || !this._config || !this._hass.connection) return;
    const key = this._config.entry_id || "";
    if (this._unsub && this._subKey === key) return;
    this._unsubscribe();
    this._subKey = key;
    const token = ++this._subToken;
    try {
      const msg = { type: WS_SUBSCRIBE };
      if (key) msg.entry_id = key;
      const unsub = await this._hass.connection.subscribeMessage((ev) => this._onEvent(ev), msg);
      if (token !== this._subToken) {
        unsub();
        return;
      }
      this._unsub = unsub;
      this._error = null;
    } catch (err) {
      this._unsub = null;
      this._subKey = null;
      this._error = err && err.code === "not_found" ? "not_found" : "error";
      this._render();
    }
  }

  _unsubscribe() {
    this._subToken += 1;
    if (this._unsub) {
      try {
        this._unsub();
      } catch (e) {
        /* Verbindung schon weg */
      }
    }
    this._unsub = null;
    this._subKey = null;
  }

  _onEvent(ev) {
    if (!ev) return;
    if (ev.type === "snapshot") {
      this._snap = ev.data;
      this._error = null;
      const fetched = this._data().fetched_at;
      if (fetched && fetched !== this._lastFetched) {
        this._lastFetched = fetched;
        const wan = this._data().wan || {};
        this._hist.down.push(Number(wan.rate_down) || 0);
        this._hist.up.push(Number(wan.rate_up) || 0);
        this._hist.down = this._hist.down.slice(-HISTORY_POINTS);
        this._hist.up = this._hist.up.slice(-HISTORY_POINTS);
      }
      this._render();
      this._renderPopup();
    } else if (ev.type === "response") {
      this._busy.delete(ev.topic);
      if (ev.status === "ok") {
        const quiet = ev.topic === "check_update";
        if (!quiet) this._showToast(this._t(ev.topic === "reboot" || ev.topic === "reconnect" ? "m_sent" : "o_saved"));
      } else {
        this._showToast(ev.error || this._t("banner_error"), true);
      }
      this._render();
    }
  }

  // --- Aktionen ---
  async _act(payload) {
    const msg = { type: WS_ACTION, ...payload };
    if (this._config.entry_id) msg.entry_id = this._config.entry_id;
    this._busy.add(payload.action);
    this._render();
    try {
      await this._hass.callWS(msg);
    } catch (err) {
      this._busy.delete(payload.action);
      this._showToast((err && err.message) || this._t("banner_error"), true);
      this._render();
    }
  }

  /** Zwei-Klick-Bestätigung statt Browser-Dialog. */
  _confirmThen(id, run) {
    if (this._confirm === id) {
      clearTimeout(this._confirmTimer);
      this._confirm = null;
      run();
      this._render();
      return;
    }
    this._confirm = id;
    clearTimeout(this._confirmTimer);
    this._confirmTimer = setTimeout(() => {
      this._confirm = null;
      this._render();
    }, CONFIRM_MS);
    this._render();
  }

  _showToast(text, isError) {
    const el = this.shadowRoot.getElementById("toast");
    if (!el) return;
    el.innerHTML = `<div class="toast${isError ? " error" : ""}" role="status">${esc(text)}</div>`;
    clearTimeout(this._toastTimer);
    this._toastTimer = setTimeout(() => {
      el.innerHTML = "";
    }, TOAST_MS);
  }

  // --- Ereignisse der Oberfläche ---
  _fromModule(e) {
    return !!(this._modBody && e.composedPath && e.composedPath().includes(this._modBody));
  }

  _onClick(e) {
    if (this._fromModule(e)) return;
    const el = e.target.closest ? e.target.closest("[data-act]") : null;
    if (!el || !this.shadowRoot.contains(el)) return;
    const act = el.dataset.act;
    const v = el.dataset.v;
    switch (act) {
      case "tab":
      case "goto":
        if (this._tabs.includes(v)) {
          this._tab = v;
          this._render();
        }
        break;
      case "wlan":
        this._openPopup("wlan", v);
        break;
      case "module":
        this._openPopup("module", v);
        break;
      case "popup_close":
        this._closePopup();
        break;
      case "backdrop":
        if (e.target === el) this._closePopup();
        break;
      case "wlan_toggle":
        if (!this._canEdit()) break;
        if (el.dataset.en === "1") this._act({ action: "set_wlan", wlan: v, enabled: true });
        else this._confirmThen(`wlan:${v}`, () => this._act({ action: "set_wlan", wlan: v, enabled: false }));
        break;
      case "check_update":
        this._act({ action: "check_update" });
        break;
      case "reboot":
        if (this._canEdit()) this._confirmThen("reboot", () => this._act({ action: "reboot" }));
        break;
      case "reconnect":
        if (this._canEdit()) this._confirmThen("reconnect", () => this._act({ action: "reconnect" }));
        break;
      case "clear_events":
        if (this._canEdit()) this._act({ action: "clear_events" });
        break;
      case "copy":
        this._copy(el.dataset.text || "");
        break;
      default:
        break;
    }
  }

  _onKeydown(e) {
    if (this._fromModule(e)) return;
    if (e.key !== "Enter" && e.key !== " ") return;
    const el = e.target.closest ? e.target.closest(".row[data-act]") : null;
    if (el && e.target === el) {
      e.preventDefault();
      el.click();
    }
  }

  _onChange(e) {
    if (this._fromModule(e)) return;
    const el = e.target;
    if (!el || !el.dataset || !el.dataset.opt || !this._canEdit()) return;
    if (el.dataset.opt === "scan_interval") {
      const value = Math.round(Number(el.value));
      if (Number.isFinite(value) && value >= 10 && value <= 600) this._act({ action: "set_option", option: "scan_interval", value });
      else this._showToast(this._t("banner_error"), true);
    } else if (el.dataset.opt === "events_enabled" || el.dataset.opt === "cpu_temperature") {
      this._act({ action: "set_option", option: el.dataset.opt, value: !!el.checked });
    }
  }

  async _copy(text) {
    try {
      await navigator.clipboard.writeText(text);
      this._showToast(this._t("b_copied"));
    } catch (e) {
      this._showToast(text);
    }
  }

  // --- Zeichnen ---
  _signature() {
    return JSON.stringify([
      this._snap, this._error, this._tab, this._confirm, [...this._busy], this._lang(),
      this._canEdit(), this._config,
    ]);
  }

  _render() {
    if (!this._config) return;
    const sig = this._signature();
    if (sig === this._sig) return;
    this._sig = sig;
    const main = this.shadowRoot.getElementById("main");
    const active = this.shadowRoot.activeElement;
    const fk = active && active.dataset ? active.dataset.fk : null;
    main.style.zoom = Number(this._config.zoom) > 0 ? String(this._config.zoom) : "1";
    main.innerHTML = this._html();
    if (fk) {
      const el = main.querySelector(`[data-fk="${fk}"]`);
      if (el) el.focus();
    }
    this._renderPopup();
  }

  _html() {
    const t = (k, p) => this._t(k, p);
    const cfg = this._config;
    const title = cfg.title === undefined ? t("default_title") : cfg.title;
    let h = "";
    if (cfg.show_title !== false && title) h += `<div class="title">${esc(title)}</div>`;
    if (this._error === "not_found") return `${h}<div class="banner error"><ha-icon icon="mdi:alert-circle"></ha-icon><div class="grow">${esc(t("not_found"))}</div></div>`;
    if (!this._snap) return `${h}<div class="empty">${esc(t("loading"))}</div>`;
    h += this._bannersHtml();
    h += this._tabsHtml();
    if (cfg.show_stats !== false && this._tab !== "settings") h += this._chipsHtml();
    const body = {
      overview: () => this._overviewHtml(),
      system: () => this._systemHtml(),
      internet: () => this._internetHtml(),
      wifi: () => this._wifiHtml(),
      modules: () => this._modulesHtml(),
      settings: () => this._settingsHtml(),
    }[this._tab];
    return h + (body ? body() : "");
  }

  // --- Banner, Tabs, Chips ---
  _mismatch() {
    const app = (this._snap && this._snap.app) || {};
    return !!app.version && app.version !== CARD_VERSION;
  }

  _bannersHtml() {
    const t = (k, p) => this._t(k, p);
    const snap = this._snap;
    const app = snap.app || {};
    let h = "";
    if (snap.reboot_pending) h += `<div class="banner live"><ha-icon icon="mdi:restart"></ha-icon><div class="grow">${esc(t("reboot_running"))}</div></div>`;
    else if (!snap.connected) h += `<div class="banner error"><ha-icon icon="mdi:lan-disconnect"></ha-icon><div class="grow">${esc(t("conn_lost"))}</div></div>`;
    if (this._mismatch()) h += `<div class="banner warning"><ha-icon icon="mdi:alert"></ha-icon><div class="grow">${esc(t("card_mismatch", { card: CARD_VERSION, integration: app.version }))}</div></div>`;
    if (app.update_available && app.latest_version) h += `<div class="banner warning"><ha-icon icon="mdi:update"></ha-icon><div class="grow">${esc(t("app_update_banner", { v: app.latest_version }))}</div></div>`;
    return h;
  }

  _badgeFor(tab) {
    const data = this._data();
    const app = (this._snap && this._snap.app) || {};
    if (tab === "internet" && data.wan && data.wan.status && data.wan.connected === false) return { cls: "error", text: "!" };
    if (tab === "system" && data.update && data.update.available) return { cls: "info", text: "1" };
    if (tab === "settings" && (app.update_available || this._mismatch())) return { cls: "warning", text: "↑" };
    return null;
  }

  _tabsHtml() {
    if (this._tabs.length < 2) return "";
    const items = this._tabs.map((tab) => {
      const meta = TAB_META[tab];
      const label = this._t(meta.label);
      const badge = this._badgeFor(tab);
      const color = this._iconColors && this._iconColors[tab] ? `style="--ic:${esc(this._iconColors[tab])}"` : "";
      return `<button class="tab${tab === this._tab ? " active" : ""}" data-act="tab" data-v="${tab}" title="${esc(label)}" aria-label="${esc(label)}" ${color}><ha-icon icon="${meta.icon}"></ha-icon><span class="lbl">${esc(label)}</span>${badge ? `<span class="badge ${badge.cls}">${esc(badge.text)}</span>` : ""}</button>`;
    });
    return `<div class="tabs" role="tablist">${items.join("")}</div>`;
  }

  _chipsHtml() {
    const t = (k, p) => this._t(k, p);
    const data = this._data();
    const wan = data.wan || {};
    const chips = [];
    const link = (tab) => (this._tabs.includes(tab) ? ` data-act="goto" data-v="${tab}"` : "");
    if (wan.status) {
      chips.push(`<span class="chip ${wan.connected ? "success" : "error"}"${link("internet")}><ha-icon icon="${wan.connected ? "mdi:web" : "mdi:web-off"}"></ha-icon>${esc(t(wan.connected ? "chip_online" : "chip_offline"))}</span>`);
    } else {
      chips.push(`<span class="chip warning"${link("internet")}><ha-icon icon="mdi:web-remove"></ha-icon>${esc(t("chip_unknown"))}</span>`);
    }
    const wlan = data.wlan || {};
    if (wlan.clients_total !== null && wlan.clients_total !== undefined) {
      chips.push(`<span class="chip"${link("wifi")}><ha-icon icon="mdi:wifi"></ha-icon>${esc(t("chip_clients", { n: wlan.clients_total }))}</span>`);
    }
    if (data.update) {
      const up = !!data.update.available;
      chips.push(`<span class="chip ${up ? "info" : "success"}"${link("system")}><ha-icon icon="${up ? "mdi:update" : "mdi:check-circle-outline"}"></ha-icon>${esc(up ? `${t("chip_fw_update")}${data.update.new_version ? ` ${data.update.new_version}` : ""}` : t("chip_fw_ok"))}</span>`);
    }
    return `<div class="chips">${chips.join("")}</div>`;
  }

  // --- Bausteine ---
  _acc(key, icon, title, body, opts = {}) {
    const open = this._open[key] !== undefined ? this._open[key] : !!opts.open;
    const variant = opts.variant ? ` ${opts.variant}` : "";
    const meta = opts.meta ? `<span class="meta">${opts.meta}</span>` : "";
    return `<details class="acc${variant}" data-k="${esc(key)}"${open ? " open" : ""}><summary><ha-icon icon="${icon}"></ha-icon><span class="grow">${esc(title)}</span>${meta}</summary><div class="acc-body">${body}</div></details>`;
  }

  _line(label, value) {
    return `<div class="line"><span class="k">${esc(label)}</span><span class="v">${value}</span></div>`;
  }

  _pill(cls, text) {
    return `<span class="pill ${cls}">${esc(text)}</span>`;
  }

  _val(v) {
    return v === null || v === undefined || v === "" ? esc(this._t("na")) : esc(v);
  }

  _rowIconStyle(tab) {
    const c = this._rowIconOverride || (this._iconColors && this._iconColors[tab]) || "";
    return c ? ` style="--ic:${esc(c)}"` : "";
  }

  // --- Übersicht ---
  _tile(titleKey, icon, body, extra = "") {
    return `<div class="tile ${extra}"><h3><ha-icon icon="${icon}"></ha-icon>${esc(this._t(titleKey))}</h3>${body}</div>`;
  }

  _enabledModules() {
    return MODULE_ORDER.filter((name) => this._config[`show_module_${name}`] !== false);
  }

  _overviewHtml() {
    const t = (k, p) => this._t(k, p);
    const lang = this._lang();
    const na = t("na");
    const data = this._data();
    const wan = data.wan || {};
    const dsl = data.dsl;
    const wlan = data.wlan || { networks: [] };
    const device = data.device || {};
    const update = data.update;
    const tiles = [];

    const online = wan.status ? !!wan.connected : null;
    const statusClass = online === null ? "warning" : online ? "success" : "error";
    const statusText = online === null ? t("chip_unknown") : t(online ? "chip_online" : "chip_offline");
    tiles.push(
      this._tile(
        "t_internet",
        online === false ? "mdi:web-off" : "mdi:web",
        `<div class="big ${statusClass}">${esc(statusText)}</div>` +
          `<div class="sub">${esc(wan.external_ip || na)}</div>` +
          `<div class="sub">${esc(t("l_conn_uptime"))}: ${esc(fmtDuration(wan.uptime, t))}</div>`
      )
    );

    const down = fmtRate(lang, wan.rate_down);
    const up = fmtRate(lang, wan.rate_up);
    tiles.push(
      this._tile(
        "t_download",
        "mdi:download-network",
        `<div class="big">${down ? `${esc(down.num)}<small>${esc(down.unit)}</small>` : esc(na)}</div>` +
          sparkline(this._hist.down, "--fbm-color-info") +
          `<div class="sub">${esc(t("l_max"))}: ${esc(rateText(lang, wan.max_down, na))}</div>`
      )
    );
    tiles.push(
      this._tile(
        "t_upload",
        "mdi:upload-network",
        `<div class="big">${up ? `${esc(up.num)}<small>${esc(up.unit)}</small>` : esc(na)}</div>` +
          sparkline(this._hist.up, "--fbm-color-success") +
          `<div class="sub">${esc(t("l_max"))}: ${esc(rateText(lang, wan.max_up, na))}</div>`
      )
    );

    const nets = wlan.networks || [];
    const active = nets.filter((n) => n.enabled).length;
    const netList = nets
      .slice(0, 4)
      .map((n) => `<span><span class="dot ${n.enabled ? "success" : ""}"></span>${esc(n.ssid || n.key)}${n.guest ? ` · ${esc(t("w_guest"))}` : ""}</span>`)
      .join("");
    tiles.push(
      this._tile(
        "t_wifi",
        "mdi:wifi",
        `<div class="big">${active}<small>/ ${nets.length} ${esc(t("l_networks"))}</small></div>` +
          `<div class="sub">${esc(t("l_clients"))}: ${this._val(wlan.clients_total)}</div>` +
          `<div class="netlist">${netList}</div>`
      )
    );

    tiles.push(
      this._tile(
        "t_box",
        "mdi:router-network",
        `<div class="big" style="font-size:1.15rem">${this._val(device.model)}</div>` +
          `<div class="sub">${esc(t("l_firmware"))}: ${this._val(device.firmware)}</div>` +
          `<div class="sub">${esc(t("l_uptime"))}: ${esc(fmtDuration(device.uptime, t))}</div>` +
          (update && update.available ? `<div style="margin-top:6px">${this._pill("info", `${t("chip_fw_update")}${update.new_version ? ` ${update.new_version}` : ""}`)}</div>` : "")
      )
    );

    tiles.push(
      this._tile(
        "t_traffic",
        "mdi:swap-vertical",
        `<div class="kv"><span>${esc(t("l_received"))}</span><span>${esc(fmtBytes(lang, wan.bytes_received, na))}</span></div>` +
          `<div class="kv"><span>${esc(t("l_sent"))}</span><span>${esc(fmtBytes(lang, wan.bytes_sent, na))}</span></div>`
      )
    );

    if (dsl) {
      const dB = (v) => (v === null || v === undefined ? na : `${numFmt(lang, v, 1)} dB`);
      tiles.push(
        this._tile(
          "t_dsl",
          "mdi:sine-wave",
          `<div class="kv"><span>${esc(t("l_noise_down"))}</span><span>${esc(dB(dsl.noise_margin_down))}</span></div>` +
            `<div class="kv"><span>${esc(t("l_noise_up"))}</span><span>${esc(dB(dsl.noise_margin_up))}</span></div>` +
            `<div class="kv"><span>${esc(t("l_atten_down"))}</span><span>${esc(dB(dsl.attenuation_down))}</span></div>` +
            `<div class="kv"><span>${esc(t("l_atten_up"))}</span><span>${esc(dB(dsl.attenuation_up))}</span></div>`
        )
      );
    }

    const mods = this._enabledModules();
    if (mods.length) {
      const buttons = mods
        .map((name) => `<button class="btn" data-act="module" data-v="${name}"><ha-icon icon="${MODULES[name].icon}"></ha-icon>${esc(t(MODULES[name].label))}</button>`)
        .join("");
      tiles.push(this._tile("t_quick", "mdi:puzzle", `<div class="actions" style="margin-top:0">${buttons}</div>`, "wide"));
    }
    return `<div class="tiles">${tiles.join("")}</div>`;
  }

  // --- Box ---
  _systemHtml() {
    const t = (k, p) => this._t(k, p);
    const lang = this._lang();
    const data = this._data();
    const device = data.device || {};
    const update = data.update;
    const system = data.system || {};
    const lan = data.lan || {};
    let info = this._line(t("l_model"), this._val(device.model));
    info += this._line(t("l_firmware"), this._val(device.firmware));
    info += this._line(t("l_hardware"), this._val(device.hardware));
    info += this._line(t("l_uptime"), esc(fmtDuration(device.uptime, t)));
    info += this._line(t("l_known"), this._val(lan.hosts_total));
    if (system.cpu_temperature !== undefined && system.cpu_temperature !== null) info += this._line(t("l_cpu"), `${esc(numFmt(lang, system.cpu_temperature, 0))} °C`);
    let h = this._acc("info", "mdi:information-outline", t("a_info"), info, { open: true });
    if (update) {
      let body = this._line(t("l_current"), this._val(device.firmware));
      if (update.available) body += this._line(t("l_new_version"), this._pill("info", update.new_version || t("chip_fw_update")));
      else body += this._line(t("l_status"), this._pill("success", t("chip_fw_ok")));
      if (update.build_type) body += this._line("Build", this._val(update.build_type));
      h += this._acc("firmware", "mdi:update", t("a_firmware"), body, { open: !!update.available });
    }
    return h;
  }

  // --- Internet ---
  _internetHtml() {
    const t = (k, p) => this._t(k, p);
    const lang = this._lang();
    const na = t("na");
    const data = this._data();
    const wan = data.wan || {};
    const dsl = data.dsl;
    const statusPill = wan.status ? this._pill(wan.connected ? "success" : "error", t(wan.connected ? "chip_online" : "chip_offline")) : this._pill("warning", t("chip_unknown"));
    let conn = this._line(t("l_status"), statusPill);
    conn += this._line(t("l_conn_uptime"), esc(fmtDuration(wan.uptime, t)));
    if (wan.link_status) conn += this._line(t("l_link"), this._pill(wan.link_status === "Up" ? "success" : "error", wan.link_status));
    if (wan.access_type) conn += this._line(t("l_access"), this._val(wan.access_type));
    if (wan.last_error) conn += this._line(t("l_last_error"), this._pill("warning", wan.last_error));
    let h = this._acc("conn", "mdi:web", t("a_conn"), conn, { open: true });

    const addr = this._line(t("l_ipv4"), this._val(wan.external_ip)) + this._line(t("l_ipv6"), this._val(wan.external_ipv6)) + this._line(t("l_prefix"), this._val(wan.ipv6_prefix));
    h += this._acc("addr", "mdi:ip-network", t("a_addresses"), addr);

    const speed =
      this._line(t("l_rate_down"), esc(rateText(lang, wan.rate_down, na))) +
      sparkline(this._hist.down, "--fbm-color-info") +
      this._line(t("l_rate_up"), esc(rateText(lang, wan.rate_up, na))) +
      sparkline(this._hist.up, "--fbm-color-success") +
      this._line(`${t("l_max")} ↓`, esc(rateText(lang, wan.max_down, na))) +
      this._line(`${t("l_max")} ↑`, esc(rateText(lang, wan.max_up, na)));
    h += this._acc("speed", "mdi:speedometer", t("a_speed"), speed, { open: true });

    const traffic = this._line(t("l_received"), esc(fmtBytes(lang, wan.bytes_received, na))) + this._line(t("l_sent"), esc(fmtBytes(lang, wan.bytes_sent, na)));
    h += this._acc("traffic", "mdi:swap-vertical", t("a_traffic"), traffic);

    if (dsl) {
      const dB = (v) => (v === null || v === undefined ? na : `${numFmt(lang, v, 1)} dB`);
      const body =
        this._line(t("l_status"), this._val(dsl.status)) +
        this._line(t("l_noise_down"), esc(dB(dsl.noise_margin_down))) +
        this._line(t("l_noise_up"), esc(dB(dsl.noise_margin_up))) +
        this._line(t("l_atten_down"), esc(dB(dsl.attenuation_down))) +
        this._line(t("l_atten_up"), esc(dB(dsl.attenuation_up)));
      h += this._acc("dsl", "mdi:sine-wave", t("a_dsl"), body);
    }
    return h;
  }

  // --- WLAN ---
  _networks() {
    return (this._data().wlan && this._data().wlan.networks) || [];
  }

  _network(key) {
    return this._networks().find((n) => n.key === key) || null;
  }

  _bandText(net) {
    return net.band ? `${net.band === "2.4" ? "2,4" : net.band} GHz` : "";
  }

  _wifiHtml() {
    const t = (k, p) => this._t(k, p);
    const nets = this._networks();
    if (!nets.length) return `<div class="empty">${esc(t("w_empty"))}</div>`;
    const canEdit = this._canEdit();
    const rows = nets.map((n) => {
      const icon = n.guest ? "mdi:wifi-star" : n.enabled ? "mdi:wifi" : "mdi:wifi-off";
      const sub = [this._bandText(n), n.channel ? `${t("w_channel")} ${n.channel}` : "", n.standard || ""].filter(Boolean).join(" · ");
      let toggle = "";
      if (canEdit) {
        const id = `wlan:${n.key}`;
        const armed = this._confirm === id;
        const busy = this._busy.has("set_wlan");
        toggle = n.enabled
          ? `<button class="btn small danger${armed ? " armed" : ""}" data-act="wlan_toggle" data-v="${esc(n.key)}" data-en="0"${busy ? " disabled" : ""}>${esc(armed ? t("m_confirm") : t("w_turn_off"))}</button>`
          : `<button class="btn small" data-act="wlan_toggle" data-v="${esc(n.key)}" data-en="1"${busy ? " disabled" : ""}>${esc(t("w_turn_on"))}</button>`;
      }
      return `<div class="row" role="button" tabindex="0" data-act="wlan" data-v="${esc(n.key)}">` +
        `<div class="ricon"${this._rowIconStyle("wifi")}><ha-icon icon="${icon}"></ha-icon><span class="dot ${n.enabled ? "success" : ""}"></span></div>` +
        `<div class="grow"><div class="rtitle">${esc(n.ssid || n.key)}${n.guest ? this._pill("info", t("w_guest")) : ""}</div><div class="rsub">${esc(sub || t("na"))}</div></div>` +
        `<div class="rend">${n.clients !== null && n.clients !== undefined ? this._pill("", `${n.clients} ${t("w_clients")}`) : ""}${toggle}</div></div>`;
    });
    return `<div class="rows">${rows.join("")}</div>`;
  }

  _wlanPopupHtml() {
    const t = (k, p) => this._t(k, p);
    const net = this._network(this._popup.key);
    if (!net) return "";
    const canEdit = this._canEdit();
    let info = this._line(t("w_status"), this._pill(net.enabled ? "success" : "", t(net.enabled ? "w_on" : "w_off")));
    info += this._line("SSID", this._val(net.ssid));
    info += this._line(t("w_type"), esc(t(net.guest ? "w_guest_net" : "w_normal")));
    info += this._line(t("w_band"), this._val(this._bandText(net)));
    info += this._line(t("w_channel"), this._val(net.channel));
    info += this._line(t("w_standard"), this._val(net.standard));
    info += this._line(t("w_clients"), this._val(net.clients));
    let body = this._acc("p_info", "mdi:information-outline", t("a_info"), info, { open: true });
    if (canEdit) {
      const id = `wlan:${net.key}`;
      const armed = this._confirm === id;
      const busy = this._busy.has("set_wlan");
      const btn = net.enabled
        ? `<button class="btn danger${armed ? " armed" : ""}" data-act="wlan_toggle" data-v="${esc(net.key)}" data-en="0"${busy ? " disabled" : ""}><ha-icon icon="mdi:wifi-off"></ha-icon>${esc(armed ? t("m_confirm") : t("w_turn_off"))}</button>`
        : `<button class="btn primary" data-act="wlan_toggle" data-v="${esc(net.key)}" data-en="1"${busy ? " disabled" : ""}><ha-icon icon="mdi:wifi"></ha-icon>${esc(t("w_turn_on"))}</button>`;
      body += this._acc("p_switch", "mdi:toggle-switch-outline", t("a_switch"), `<div class="actions" style="margin-top:0">${btn}</div>${net.enabled ? `<p class="hint warn">${esc(t("w_off_warn"))}</p>` : ""}`, { open: true });
    }
    body += this._acc("p_diag", "mdi:bug-outline", t("a_diag"), this._line("Key", this._val(net.key)) + this._line("Status", this._val(net.status)) + `<p class="hint">${esc(t("w_guest_hint"))}</p>`);
    const icon = net.guest ? "mdi:wifi-star" : net.enabled ? "mdi:wifi" : "mdi:wifi-off";
    return `<div class="backdrop" data-act="backdrop"><div class="popup" role="dialog" aria-modal="true" aria-label="${esc(net.ssid || net.key)}"><div class="phead"><ha-icon icon="${icon}"></ha-icon><div class="ptitle">${esc(net.ssid || net.key)}</div><button class="btn icon" data-act="popup_close" aria-label="${esc(t("b_close"))}" title="${esc(t("b_close"))}"><ha-icon icon="mdi:close"></ha-icon></button></div><div class="pbody">${body}</div></div></div>`;
  }

  // --- Module ---
  _moduleStatus(name) {
    const def = MODULES[name];
    const loaded = !!(window.customElements && window.customElements.get(def.tag));
    const detected = detectModuleEntities(this._hass, def);
    const override = this._config[`module_${name}_config`];
    const config = { ...detected, ...(override && typeof override === "object" ? override : {}) };
    const missingKeys = Object.keys(def.keys).filter((k) => !config[k]);
    let state = "ready";
    if (!loaded) state = "missing";
    else if (missingKeys.length) state = "noentity";
    return { state, config, missingKeys, def };
  }

  _modulesHtml() {
    const t = (k, p) => this._t(k, p);
    const names = this._enabledModules();
    if (!names.length) return `<div class="empty">${esc(t("na"))}</div>`;
    const rows = names.map((name) => {
      const st = this._moduleStatus(name);
      const pill = st.state === "ready" ? this._pill("success", t("mod_ready")) : this._pill("warning", t(st.state === "missing" ? "mod_missing" : "mod_noentity"));
      return `<div class="row" role="button" tabindex="0" data-act="module" data-v="${name}"><div class="ricon"${this._rowIconStyle("modules")}><ha-icon icon="${st.def.icon}"></ha-icon></div><div class="grow"><div class="rtitle">${esc(t(st.def.label))}</div><div class="rsub">${esc(t(st.def.desc))}</div></div><div class="rend">${pill}<ha-icon icon="mdi:open-in-new"></ha-icon></div></div>`;
    });
    return `<div class="rows">${rows.join("")}</div>`;
  }

  _moduleHelpHtml(name, st) {
    const t = (k, p) => this._t(k, p);
    const label = t(st.def.label);
    let h = `<div class="helpbox">`;
    if (st.state === "missing") h += `<p>${esc(t("mod_missing_text", { name: label }))}</p>`;
    else if (st.state === "noentity") {
      const key = `module_${name}_config`;
      const yaml = `${key}:\n${Object.keys(st.def.keys).map((k) => `  ${k}: sensor.…`).join("\n")}`;
      h += `<p>${esc(t("mod_noentity_text", { name: label, key }))}</p><div class="code">${esc(yaml)}</div><button class="btn small" data-act="copy" data-text="${esc(yaml)}"><ha-icon icon="mdi:content-copy"></ha-icon>${esc(t("b_copy"))}</button>`;
    } else h += `<p>${esc(t("mod_error_text", { name: label }))}</p>`;
    h += `<p><a class="link" href="${esc(st.def.repo)}" target="_blank" rel="noopener noreferrer">${esc(t("mod_repo"))}</a></p></div>`;
    return h;
  }

  _modulePopupShell(name) {
    const t = (k, p) => this._t(k, p);
    const def = MODULES[name];
    return `<div class="backdrop" data-act="backdrop"><div class="popup wide" role="dialog" aria-modal="true" aria-label="${esc(t(def.label))}"><div class="phead"><ha-icon icon="${def.icon}"></ha-icon><div class="ptitle">${esc(t(def.label))}</div><button class="btn icon" data-act="popup_close" aria-label="${esc(t("b_close"))}" title="${esc(t("b_close"))}"><ha-icon icon="mdi:close"></ha-icon></button></div><div class="pbody module" id="modbody"><div class="empty">${esc(t("loading"))}</div></div></div></div>`;
  }

  async _mountModule(name) {
    const body = this._modBody;
    const st = this._moduleStatus(name);
    if (!body) return;
    if (st.state !== "ready") {
      body.classList.remove("module");
      body.innerHTML = this._moduleHelpHtml(name, st);
      return;
    }
    try {
      const cfg = { type: `custom:${st.def.tag}`, ...st.config };
      let el;
      if (typeof window.loadCardHelpers === "function") {
        const helpers = await window.loadCardHelpers();
        el = helpers.createCardElement(cfg);
      } else {
        el = document.createElement(st.def.tag);
        el.setConfig(cfg);
      }
      if (this._modBody !== body) return; // Popup wurde inzwischen geschlossen
      el.hass = this._hass;
      body.replaceChildren(el);
      this._modEl = el;
    } catch (err) {
      if (this._modBody !== body) return;
      body.classList.remove("module");
      body.innerHTML = this._moduleHelpHtml(name, { ...st, state: "error" });
    }
  }

  // --- Popup-Verwaltung ---
  _openPopup(kind, key) {
    if (kind === "module" && !MODULES[key]) return;
    this._popup = { kind, key };
    this._popupSig = "";
    this._renderPopup();
  }

  _closePopup() {
    this._popup = null;
    this._popupSig = "";
    this._modEl = null;
    this._modBody = null;
    const host = this.shadowRoot.getElementById("popup");
    if (host) host.innerHTML = "";
  }

  _renderPopup() {
    const host = this.shadowRoot.getElementById("popup");
    if (!host) return;
    if (!this._popup) {
      if (host.innerHTML) host.innerHTML = "";
      return;
    }
    if (this._popup.kind === "wlan") {
      if (!this._network(this._popup.key)) {
        this._closePopup();
        return;
      }
      const sig = JSON.stringify([this._popup, this._network(this._popup.key), this._confirm, [...this._busy], this._lang(), this._canEdit()]);
      if (sig === this._popupSig) return;
      this._popupSig = sig;
      const old = host.querySelector(".pbody");
      const scroll = old ? old.scrollTop : 0;
      host.innerHTML = this._wlanPopupHtml();
      const fresh = host.querySelector(".pbody");
      if (fresh) fresh.scrollTop = scroll;
    } else if (this._popup.kind === "module") {
      const sig = `module:${this._popup.key}:${this._lang()}`;
      if (sig === this._popupSig) return;
      this._popupSig = sig;
      host.innerHTML = this._modulePopupShell(this._popup.key);
      this._modBody = host.querySelector("#modbody");
      this._mountModule(this._popup.key);
    }
  }

  // --- Einstellungen (Zahnrad) ---
  _eventText(ev) {
    const p = ev.params || {};
    const key = ev.kind === "wlan_changed" ? (p.enabled ? "ev_wlan_changed_on" : "ev_wlan_changed_off") : `ev_${ev.kind}`;
    return this._t(key, { version: p.version, wlan: p.wlan, option: p.option });
  }

  _settingsHtml() {
    const t = (k, p) => this._t(k, p);
    const lang = this._lang();
    const na = t("na");
    const snap = this._snap;
    const app = snap.app || {};
    const canEdit = this._canEdit();
    const mismatch = this._mismatch();
    const needsUpdate = !!app.update_available || mismatch;

    // 1. App-Version (immer zuerst, offen)
    let ver = this._line(t("v_integration"), this._val(app.version));
    ver += this._line(t("v_card"), mismatch ? this._pill("warning", CARD_VERSION) : esc(CARD_VERSION));
    ver += this._line(t("v_latest"), this._val(app.latest_version));
    let state;
    if (app.check_failed && !app.latest_version) state = this._pill("error", t("v_failed"));
    else if (app.update_available) state = this._pill("warning", t("v_update"));
    else if (mismatch) state = this._pill("warning", t("card_mismatch", { card: CARD_VERSION, integration: app.version }));
    else if (app.checked_at) state = this._pill("success", t("v_up_to_date"));
    else state = esc(t("v_never"));
    ver += this._line(t("l_status"), state);
    ver += this._line(t("v_checked"), esc(app.checked_at ? fmtRelative(lang, app.checked_at, na) : t("v_never")));
    if (needsUpdate) ver += `<p class="hint warn">${esc(t("v_hint"))}</p>`;
    if (/(a|b|rc)\d+$/.test(CARD_VERSION)) ver += `<p class="hint">${esc(t("v_beta_hint"))}</p>`;
    const releaseUrl = typeof app.release_url === "string" && app.release_url.startsWith("https://github.com/") ? app.release_url : GITHUB_RELEASES;
    ver += `<div class="actions">${canEdit ? `<button class="btn" data-act="check_update"${this._busy.has("check_update") ? " disabled" : ""}><ha-icon icon="mdi:refresh"></ha-icon>${esc(t("v_check_now"))}</button>` : ""}<a class="btn" href="${esc(releaseUrl)}" target="_blank" rel="noopener noreferrer"><ha-icon icon="mdi:github"></ha-icon>${esc(t("v_release"))}</a></div>`;
    let h = this._acc("app", "mdi:information", t("a_app"), ver, { open: true, variant: needsUpdate ? "update" : "", meta: esc(app.version || "") });

    // 2. Verbindung (offen)
    const stateLine = snap.connected ? this._pill("success", t("c_connected")) : this._pill("error", t("c_disconnected"));
    let conn = this._line(t("c_state"), stateLine);
    if (snap.host) conn += this._line(t("c_host"), esc(snap.host));
    if (snap.host) conn += this._line(t("c_secure"), esc(t(snap.ssl ? "c_yes" : "c_no")));
    conn += this._line(t("c_updated"), esc(fmtRelative(lang, this._data().fetched_at, na)));
    conn += this._line(t("c_interval"), esc(`${(snap.options || {}).scan_interval || na} s`));
    const errs = Object.keys(this._data().errors || {});
    if (errs.length) conn += this._line("!", this._pill("warning", errs.join(", ")));
    h += this._acc("box_conn", "mdi:lan-connect", t("a_box_conn"), conn, { open: true });

    // 3. Optionen
    const opts = snap.options || {};
    let optBody;
    if (canEdit) {
      optBody =
        `<div class="field"><label for="o-scan">${esc(t("o_scan"))}</label><input id="o-scan" type="number" min="10" max="600" step="1" value="${esc(opts.scan_interval)}" data-opt="scan_interval" data-fk="scan"></div>` +
        `<div class="field"><label for="o-ev">${esc(t("o_events"))}<div class="hint">${esc(t("o_events_hint"))}</div></label><input id="o-ev" type="checkbox" data-opt="events_enabled" data-fk="ev"${opts.events_enabled ? " checked" : ""}></div>` +
        `<div class="field"><label for="o-cpu">${esc(t("o_cpu"))}<div class="hint">${esc(t("o_cpu_hint"))}</div></label><input id="o-cpu" type="checkbox" data-opt="cpu_temperature" data-fk="cpu"${opts.cpu_temperature ? " checked" : ""}></div>`;
    } else {
      optBody =
        this._line(t("o_scan"), esc(opts.scan_interval)) +
        this._line(t("o_events"), esc(t(opts.events_enabled ? "c_yes" : "c_no"))) +
        this._line(t("o_cpu"), esc(t(opts.cpu_temperature ? "c_yes" : "c_no"))) +
        `<p class="hint">${esc(t(this._config.read_only ? "o_readonly" : "o_admin"))}</p>`;
    }
    h += this._acc("options", "mdi:tune", t("a_options"), optBody);

    // 4. Wartung (Neustart, Neu verbinden - mit Zwei-Klick-Bestätigung)
    let maint;
    if (canEdit) {
      const rb = this._confirm === "reboot";
      const rc = this._confirm === "reconnect";
      maint =
        `<div class="field"><div>${esc(t("m_reconnect"))}<div class="hint">${esc(t("m_reconnect_hint"))}</div></div><button class="btn danger${rc ? " armed" : ""}" data-act="reconnect"${this._busy.has("reconnect") ? " disabled" : ""}><ha-icon icon="mdi:web-refresh"></ha-icon>${esc(rc ? t("m_confirm") : t("m_reconnect"))}</button></div>` +
        `<div class="field"><div>${esc(t("m_reboot"))}<div class="hint">${esc(t("m_reboot_hint"))}</div></div><button class="btn danger${rb ? " armed" : ""}" data-act="reboot"${this._busy.has("reboot") ? " disabled" : ""}><ha-icon icon="mdi:restart"></ha-icon>${esc(rb ? t("m_confirm") : t("m_reboot"))}</button></div>`;
    } else {
      maint = `<p class="hint">${esc(t(this._config.read_only ? "o_readonly" : "o_admin"))}</p>`;
    }
    h += this._acc("maintenance", "mdi:wrench", t("a_maintenance"), maint, { variant: "danger" });

    // 5. Ereignisse seit dem Start
    const events = snap.events || [];
    const max = Math.max(1, Number(this._config.max_rows) || 20);
    let evBody;
    if (!events.length) evBody = `<div class="empty">${esc(t("ev_empty"))}</div>`;
    else {
      evBody = events
        .slice(0, max)
        .map((ev) => `<div class="ev"><span class="dot ${EVENT_SEVERITY[ev.kind] || ""}"></span><div class="grow">${esc(this._eventText(ev))}</div><span class="muted" title="${esc(fmtDateTime(lang, ev.time, na))}">${esc(fmtRelative(lang, ev.time, na))}</span></div>`)
        .join("");
      if (events.length > max) evBody += `<p class="hint">${esc(t("ev_more", { n: events.length - max }))}</p>`;
      if (canEdit) evBody += `<div class="actions"><button class="btn small" data-act="clear_events"><ha-icon icon="mdi:delete-sweep"></ha-icon>${esc(t("ev_clear"))}</button></div>`;
    }
    h += this._acc("events", "mdi:history", t("a_events"), evBody, { meta: String(events.length) });
    return h;
  }
}

// --- Karten-Editor --------------------------------------------------------------
const EDITOR_LABELS = {
  title: "Titel (leer = keine Überschrift)",
  show_title: "Titel anzeigen",
  entry_id: "Eintrags-ID (nur bei mehreren FRITZ!Boxen)",
  show_overview: "Kategorie „Übersicht“ anzeigen",
  show_system: "Kategorie „Box“ anzeigen",
  show_internet: "Kategorie „Internet“ anzeigen",
  show_wifi: "Kategorie „WLAN“ anzeigen",
  show_modules: "Kategorie „Module“ anzeigen",
  show_settings: "Kategorie „Einstellungen“ anzeigen",
  default_tab: "Starttab",
  max_rows: "Ereignisse im Protokoll (höchstens)",
  zoom: "Zoom der Karte",
  show_stats: "Statistik-Chips anzeigen",
  read_only: "Nur Ansicht (Bedienelemente ausblenden)",
  show_module_calls: "Modul „Anrufe“ anzeigen",
  show_module_network: "Modul „Netzwerk“ anzeigen",
  show_module_events: "Modul „Ereignisse“ anzeigen",
  module_calls_config: "Anrufe: Karten-Konfiguration überschreiben (optional)",
  module_network_config: "Netzwerk: Karten-Konfiguration überschreiben (optional)",
  module_events_config: "Ereignisse: Karten-Konfiguration überschreiben (optional)",
};
const EDITOR_COLOR_LABELS = {
  tab_active: "Aktiver Tab", success: "Erfolg (grün)", warning: "Warnung (orange)", error: "Fehler (rot)", info: "Info (blau)",
  row_icon: "Zeilensymbole (alle Kategorien)", live_banner: "Live-Banner",
  icon_overview: "Symbol „Übersicht“", icon_system: "Symbol „Box“", icon_internet: "Symbol „Internet“", icon_wifi: "Symbol „WLAN“", icon_modules: "Symbol „Module“", icon_settings: "Symbol „Einstellungen“",
};

class FritzboxManagerCardEditor extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
    this._hass = null;
    this._app = null;
    this._unsub = null;
    this._built = false;
  }

  connectedCallback() {
    if (this._hass && !this._unsub && !this._app) this._probe();
  }

  disconnectedCallback() {
    if (this._unsub) {
      try {
        this._unsub();
      } catch (e) {
        /* bereits getrennt */
      }
      this._unsub = null;
    }
  }

  setConfig(config) {
    this._config = { ...config };
    this._render();
  }

  set hass(hass) {
    const first = !this._hass;
    this._hass = hass;
    if (this._form) this._form.hass = hass;
    if (first) this._probe();
  }

  /** Holt einmalig die Versionsangaben der Integration für den Infoblock. */
  async _probe() {
    if (!this._hass || !this._hass.connection) return;
    try {
      const msg = { type: WS_SUBSCRIBE };
      if (this._config.entry_id) msg.entry_id = this._config.entry_id;
      let done = false;
      const unsub = await this._hass.connection.subscribeMessage((ev) => {
        if (done || !ev || ev.type !== "snapshot") return;
        done = true;
        this._app = ev.data.app || {};
        this._renderInfo();
        Promise.resolve().then(() => {
          try {
            unsub();
          } catch (e) {
            /* ignorieren */
          }
          this._unsub = null;
        });
      }, msg);
      this._unsub = unsub;
    } catch (e) {
      this._app = { error: true };
      this._renderInfo();
    }
  }

  _formKeys() {
    const keys = [];
    for (const group of this._schema()) for (const field of group.schema) keys.push(field.name);
    return keys;
  }

  _schema() {
    const tabOptions = TAB_ORDER.map((k) => ({ value: k, label: I18N.de[TAB_META[k].label] }));
    return [
      {
        type: "expandable", name: "", title: "Kategorien", icon: "mdi:tab", expanded: true, flatten: true,
        schema: [
          ...TAB_ORDER.map((k) => ({ name: `show_${k}`, selector: { boolean: {} } })),
          { name: "default_tab", selector: { select: { mode: "dropdown", options: tabOptions } } },
        ],
      },
      {
        type: "expandable", name: "", title: "Module (Popups)", icon: "mdi:puzzle", flatten: true,
        schema: [
          ...MODULE_ORDER.map((k) => ({ name: `show_module_${k}`, selector: { boolean: {} } })),
          ...MODULE_ORDER.map((k) => ({ name: `module_${k}_config`, selector: { object: {} } })),
        ],
      },
      {
        type: "expandable", name: "", title: "Darstellung", icon: "mdi:palette-swatch", flatten: true,
        schema: [
          { name: "title", selector: { text: {} } },
          { name: "show_title", selector: { boolean: {} } },
          { name: "show_stats", selector: { boolean: {} } },
          { name: "max_rows", selector: { number: { min: 1, max: 100, mode: "box" } } },
          { name: "zoom", selector: { number: { min: 0.5, max: 2, step: 0.05, mode: "slider" } } },
          { name: "entry_id", selector: { text: {} } },
        ],
      },
      {
        type: "expandable", name: "", title: "Bearbeiten", icon: "mdi:pencil-lock", flatten: true,
        schema: [{ name: "read_only", selector: { boolean: {} } }],
      },
    ];
  }

  _render() {
    if (!this._built) {
      this.shadowRoot.innerHTML = `<style>
        :host { display: block; }
        .info { padding: 10px 12px; margin: 0 0 12px; border-radius: 8px; border: 1px solid var(--divider-color); font-size: .92rem; }
        .info.warn { border-color: var(--warning-color, #ff9800); background: color-mix(in srgb, var(--warning-color, #ff9800) 12%, transparent); }
        .info .status { margin-top: 4px; color: var(--secondary-text-color); }
        details { border: 1px solid var(--divider-color); border-radius: 8px; margin-top: 12px; }
        summary { cursor: pointer; padding: 10px 12px; font-weight: 500; }
        .colors { padding: 4px 12px 12px; display: grid; gap: 8px; }
        .crow { display: grid; grid-template-columns: 1fr auto 150px; align-items: center; gap: 8px; }
        .crow input[type=text] { padding: 6px 8px; border-radius: 6px; border: 1px solid var(--divider-color); background: var(--card-background-color, transparent); color: var(--primary-text-color); font: inherit; }
        .crow input[type=color] { width: 36px; height: 30px; padding: 0; border: 1px solid var(--divider-color); border-radius: 6px; background: none; }
        button { margin-top: 8px; padding: 6px 12px; border-radius: 6px; border: 1px solid var(--divider-color); background: transparent; color: var(--primary-text-color); font: inherit; cursor: pointer; }
      </style><div id="info"></div><ha-form id="form"></ha-form><details id="colors"><summary>Farben</summary><div class="colors" id="colorbody"></div></details>`;
      this._form = this.shadowRoot.getElementById("form");
      this._form.computeLabel = (schema) => EDITOR_LABELS[schema.name] || schema.name;
      this._form.addEventListener("value-changed", (ev) => this._onForm(ev));
      this.shadowRoot.getElementById("colorbody").addEventListener("input", (ev) => this._onColor(ev));
      this.shadowRoot.getElementById("colorbody").addEventListener("click", (ev) => {
        if (ev.target && ev.target.dataset && ev.target.dataset.reset) this._resetColors();
      });
      this._built = true;
    }
    this._form.hass = this._hass;
    this._form.schema = this._schema();
    this._form.data = { ...CONFIG_DEFAULTS, ...this._config, title: this._config.title === undefined ? I18N.de.default_title : this._config.title };
    this._renderInfo();
    this._renderColors();
  }

  _renderInfo() {
    const box = this.shadowRoot.getElementById("info");
    if (!box) return;
    const app = this._app;
    let status = "…";
    let warn = false;
    let integration = "—";
    if (app && app.error) status = "Keine Verbindung zur Integration (noch nicht eingerichtet?)";
    else if (app) {
      integration = app.version || "—";
      if (app.update_available && app.latest_version) {
        status = `Neue Version ${app.latest_version} verfügbar. Aktualisiere über HACS und starte Home Assistant neu. Danach Browser neu laden (Strg+F5).`;
        warn = true;
      } else if (app.version && app.version !== CARD_VERSION) {
        status = "Karte und Integration haben verschiedene Versionen. Browser-Cache leeren (Strg+F5).";
        warn = true;
      } else if (app.check_failed && !app.latest_version) status = "Versionsprüfung nicht möglich";
      else if (app.checked_at) status = "Aktuell";
    }
    box.innerHTML = `<div class="info${warn ? " warn" : ""}"><strong>Karte ${esc(CARD_VERSION)} · Integration ${esc(integration)}</strong><div class="status">${esc(status)}</div></div>`;
  }

  _fire(config) {
    this._config = config;
    this.dispatchEvent(new CustomEvent("config-changed", { detail: { config }, bubbles: true, composed: true }));
  }

  _onForm(ev) {
    ev.stopPropagation();
    const value = { ...ev.detail.value };
    // Ein bewusst geleerter Titel wird als "" gespeichert (sonst greift der Standardtitel wieder).
    if (value.title === undefined && this._config.title !== undefined) value.title = "";
    if (value.title === I18N.de.default_title && this._config.title === undefined) delete value.title;
    const next = { ...this._config };
    for (const [k, v] of Object.entries(value)) {
      if (v === undefined || (typeof v === "object" && v !== null && !Array.isArray(v) && Object.keys(v).length === 0 && k.startsWith("module_"))) delete next[k];
      else next[k] = v;
    }
    // Nur Schlüssel entfernen, die das Formular kennt (fremde Schlüssel wie card_mod bleiben erhalten).
    for (const k of this._formKeys()) if (!(k in value) && k !== "title") delete next[k];
    next.type = this._config.type || "custom:fritzbox-manager-card";
    this._fire(next);
  }

  _colorKeys() {
    return [...Object.keys(COLOR_CONFIG_KEYS).map((k) => `color_${k}`), ...TAB_ORDER.map((k) => CATEGORY_ICON_COLOR_KEYS[k])];
  }

  _renderColors() {
    const body = this.shadowRoot.getElementById("colorbody");
    if (!body || body.contains(this.shadowRoot.activeElement)) return;
    const rows = this._colorKeys().map((key) => {
      const label = EDITOR_COLOR_LABELS[key.replace(/^color_/, "")] || key;
      const cur = this._config[key] || "";
      const hex = /^#[0-9a-fA-F]{6}$/.test(cur) ? cur : "#888888";
      return `<div class="crow"><span>${esc(label)}</span><input type="color" value="${esc(hex)}" data-ckey="${esc(key)}" aria-label="${esc(label)}"><input type="text" value="${esc(cur)}" placeholder="Theme-Standard" data-ckey="${esc(key)}" data-fk="c_${esc(key)}" aria-label="${esc(label)}"></div>`;
    });
    body.innerHTML = rows.join("") + `<button type="button" data-reset="1">Alle Farben zurücksetzen</button>`;
  }

  _onColor(ev) {
    const el = ev.target;
    if (!el || !el.dataset || !el.dataset.ckey) return;
    const key = el.dataset.ckey;
    const raw = String(el.value || "").trim();
    const next = { ...this._config };
    const clean = sanitizeColor(raw);
    if (clean) next[key] = clean;
    else delete next[key];
    if (el.type === "color") {
      const text = this.shadowRoot.querySelector(`input[type=text][data-ckey="${key}"]`);
      if (text) text.value = clean;
    }
    this._fire(next);
  }

  _resetColors() {
    const next = { ...this._config };
    for (const k of this._colorKeys()) delete next[k];
    this._fire(next);
    const body = this.shadowRoot.getElementById("colorbody");
    if (body) body.innerHTML = "";
    this._renderColors();
  }
}

// --- Registrierung --------------------------------------------------------------
// Doppelte Ladevorgänge (z. B. zwei Ressourceneinträge) dürfen nicht werfen.
if (!customElements.get("fritzbox-manager-card")) customElements.define("fritzbox-manager-card", FritzboxManagerCard);
if (!customElements.get("fritzbox-manager-card-editor")) customElements.define("fritzbox-manager-card-editor", FritzboxManagerCardEditor);

window.customCards = window.customCards || [];
if (!window.customCards.some((card) => card.type === "fritzbox-manager-card")) {
  window.customCards.push({
    type: "fritzbox-manager-card",
    name: "FRITZ!Box Manager",
    description: "Systemdaten der FRITZ!Box (Internet, WLAN, Firmware) in Kategorien – mit den Karten Anrufe, Netzwerk und Ereignisse als Popup.",
    preview: false,
    documentationURL: GITHUB_REPO,
  });
  // eslint-disable-next-line no-console
  console.info(
    `%c FRITZBOX-MANAGER-CARD %c v${CARD_VERSION} `,
    "color: #fff; background: #3b6642; font-weight: 700;",
    "color: #3b6642; background: #fff; font-weight: 700;"
  );
}
