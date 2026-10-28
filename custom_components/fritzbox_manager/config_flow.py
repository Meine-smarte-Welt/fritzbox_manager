# SHA256 (Inhalt ab Zeile 2, d.h. dieser Datei ohne diese erste Zeile): 22468894b466324806a33afb95e586e728fd0a0a3d155fb2fca2231ad2b00ae7
"""Config Flow: Einrichtung, Anmeldung erneuern, Neu konfigurieren, Optionen."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_SSL, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    BooleanSelector,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
)

from .const import (
    CONF_CPU_TEMPERATURE,
    CONF_EVENTS_ENABLED,
    CONF_SCAN_INTERVAL,
    DEFAULT_CPU_TEMPERATURE,
    DEFAULT_EVENTS_ENABLED,
    DEFAULT_HOST,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_USERNAME,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
    VERSION,
)
from .fritz_client import FritzCannotConnect, FritzClient, FritzInvalidAuth

_LOGGER = logging.getLogger(__name__)


def _connection_schema(defaults: dict[str, Any], *, with_host: bool = True) -> vol.Schema:
    fields: dict[Any, Any] = {}
    if with_host:
        fields[vol.Required(CONF_HOST, default=defaults.get(CONF_HOST, DEFAULT_HOST))] = str
        port_key = (
            vol.Optional(CONF_PORT, default=defaults[CONF_PORT])
            if defaults.get(CONF_PORT)
            else vol.Optional(CONF_PORT)
        )
        fields[port_key] = vol.All(vol.Coerce(int), vol.Range(min=1, max=65535))
    fields[vol.Required(CONF_USERNAME, default=defaults.get(CONF_USERNAME, DEFAULT_USERNAME))] = str
    fields[vol.Required(CONF_PASSWORD, default=defaults.get(CONF_PASSWORD, ""))] = str
    if with_host:
        fields[vol.Required(CONF_SSL, default=bool(defaults.get(CONF_SSL, False)))] = bool
    return vol.Schema(fields)


async def _async_validate(hass, data: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    """Verbindung prüfen. Gibt (Geräteinfo, Fehlerschlüssel) zurück."""
    client = FritzClient(
        data[CONF_HOST],
        data.get(CONF_PORT),
        data.get(CONF_USERNAME),
        data.get(CONF_PASSWORD),
        data.get(CONF_SSL, False),
    )
    try:
        info = await hass.async_add_executor_job(client.connect)
    except FritzInvalidAuth:
        return {}, "invalid_auth"
    except FritzCannotConnect:
        return {}, "cannot_connect"
    except Exception:  # noqa: BLE001 - Einrichtung soll nie mit einem Absturz enden
        _LOGGER.exception("Unerwarteter Fehler bei der Prüfung der FRITZ!Box")
        return {}, "unknown"
    finally:
        client.close()
    return info, None


class FritzboxManagerConfigFlow(ConfigFlow, domain=DOMAIN):
    """Einrichtung einer FRITZ!Box."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry) -> FritzOptionsFlow:
        return FritzOptionsFlow()

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        defaults = user_input or {}
        if user_input is not None:
            data = {k: v for k, v in user_input.items() if v not in (None, "")}
            info, error = await _async_validate(self.hass, data)
            if error:
                errors["base"] = error
            else:
                await self.async_set_unique_id(info.get("serial") or data[CONF_HOST])
                self._abort_if_unique_id_configured(updates=data)
                title = info.get("model") or "FRITZ!Box"
                return self.async_create_entry(title=title, data=data)
        return self.async_show_form(
            step_id="user", data_schema=_connection_schema(defaults), errors=errors
        )

    async def async_step_reauth(self, entry_data: dict[str, Any]) -> ConfigFlowResult:
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        entry = self._get_reauth_entry()
        errors: dict[str, str] = {}
        if user_input is not None:
            data = {**entry.data, **{k: v for k, v in user_input.items() if v not in (None, "")}}
            _info, error = await _async_validate(self.hass, data)
            if error:
                errors["base"] = error
            else:
                return self.async_update_reload_and_abort(entry, data=data)
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=_connection_schema(dict(entry.data), with_host=False),
            errors=errors,
            description_placeholders={"host": entry.data[CONF_HOST]},
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}
        if user_input is not None:
            data = {k: v for k, v in user_input.items() if v not in (None, "")}
            info, error = await _async_validate(self.hass, data)
            if error:
                errors["base"] = error
            else:
                await self.async_set_unique_id(info.get("serial") or data[CONF_HOST])
                self._abort_if_unique_id_mismatch()
                return self.async_update_reload_and_abort(entry, data=data)
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=_connection_schema(user_input or dict(entry.data)),
            errors=errors,
        )


class FritzOptionsFlow(OptionsFlow):
    """Optionen („Konfigurieren“)."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(
                data={
                    CONF_SCAN_INTERVAL: int(user_input[CONF_SCAN_INTERVAL]),
                    CONF_EVENTS_ENABLED: bool(user_input[CONF_EVENTS_ENABLED]),
                    CONF_CPU_TEMPERATURE: bool(user_input[CONF_CPU_TEMPERATURE]),
                }
            )
        options = self.config_entry.options
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=MIN_SCAN_INTERVAL,
                        max=MAX_SCAN_INTERVAL,
                        step=1,
                        mode=NumberSelectorMode.BOX,
                        unit_of_measurement="s",
                    )
                ),
                vol.Required(
                    CONF_EVENTS_ENABLED,
                    default=options.get(CONF_EVENTS_ENABLED, DEFAULT_EVENTS_ENABLED),
                ): BooleanSelector(),
                vol.Required(
                    CONF_CPU_TEMPERATURE,
                    default=options.get(CONF_CPU_TEMPERATURE, DEFAULT_CPU_TEMPERATURE),
                ): BooleanSelector(),
            }
        )
        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            description_placeholders={
                "version": VERSION,
                "update_info": self._update_info(),
            },
        )

    def _update_info(self) -> str:
        """Kurzer Hinweistext zur Version, in der Sprache von Home Assistant."""
        lang = (self.hass.config.language or "en").split("-")[0]
        texts = {
            "de": ("Neue Version {v} verfügbar. Aktualisiere über HACS.", "Du nutzt die neueste bekannte Version.", "Versionsprüfung noch nicht erfolgt oder nicht möglich."),
            "nl": ("Nieuwe versie {v} beschikbaar. Werk bij via HACS.", "Je gebruikt de nieuwste bekende versie.", "Versiecontrole nog niet uitgevoerd of niet mogelijk."),
            "en": ("New version {v} available. Update via HACS.", "You are on the latest known version.", "Version check not done yet or not possible."),
        }
        newer, current, unknown = texts.get(lang, texts["en"])
        runtime = getattr(self.config_entry, "runtime_data", None)
        info = runtime.update_checker.info if runtime else {}
        if info.get("update_available") and info.get("latest_version"):
            return newer.format(v=info["latest_version"])
        if info.get("checked_at") and not info.get("check_failed"):
            return current
        return unknown
