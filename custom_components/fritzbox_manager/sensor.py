# SHA256 (Inhalt ab Zeile 2, d.h. dieser Datei ohne diese erste Zeile): f61bedf99d9db7b43148a06d0ea2096e0915fcb4c399336c7f615c7e9a1349e0
"""Sensoren: Systemdaten, Internet, Geschwindigkeit, Datenmenge, DSL, WLAN."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    EntityCategory,
    UnitOfDataRate,
    UnitOfInformation,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import FritzConfigEntry
from .entity import FritzEntity


@dataclass(frozen=True, kw_only=True)
class FritzSensorDescription(SensorEntityDescription):
    """Beschreibung eines Sensors: Abschnitt der Daten und Lesefunktion."""

    section: str
    value_fn: Callable[[dict[str, Any]], Any]
    # Entität nur anlegen, wenn die Box beim Start Werte dafür geliefert hat.
    require_value: bool = False


def _get(key: str) -> Callable[[dict[str, Any]], Any]:
    return lambda section: section.get(key)


SENSORS: tuple[FritzSensorDescription, ...] = (
    FritzSensorDescription(
        key="firmware",
        section="device",
        value_fn=_get("firmware"),
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    FritzSensorDescription(
        key="uptime",
        section="device",
        value_fn=_get("uptime"),
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        suggested_unit_of_measurement=UnitOfTime.HOURS,
        suggested_display_precision=0,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    FritzSensorDescription(
        key="connection_uptime",
        section="wan",
        value_fn=_get("uptime"),
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        suggested_unit_of_measurement=UnitOfTime.HOURS,
        suggested_display_precision=0,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    FritzSensorDescription(
        key="external_ip",
        section="wan",
        value_fn=_get("external_ip"),
    ),
    FritzSensorDescription(
        key="external_ipv6",
        section="wan",
        value_fn=_get("external_ipv6"),
        entity_registry_enabled_default=False,
    ),
    FritzSensorDescription(
        key="ipv6_prefix",
        section="wan",
        value_fn=_get("ipv6_prefix"),
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    FritzSensorDescription(
        key="download_rate",
        section="wan",
        value_fn=_get("rate_down"),
        device_class=SensorDeviceClass.DATA_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfDataRate.BITS_PER_SECOND,
        suggested_unit_of_measurement=UnitOfDataRate.MEGABITS_PER_SECOND,
        suggested_display_precision=2,
    ),
    FritzSensorDescription(
        key="upload_rate",
        section="wan",
        value_fn=_get("rate_up"),
        device_class=SensorDeviceClass.DATA_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfDataRate.BITS_PER_SECOND,
        suggested_unit_of_measurement=UnitOfDataRate.MEGABITS_PER_SECOND,
        suggested_display_precision=2,
    ),
    FritzSensorDescription(
        key="max_download_rate",
        section="wan",
        value_fn=_get("max_down"),
        device_class=SensorDeviceClass.DATA_RATE,
        native_unit_of_measurement=UnitOfDataRate.BITS_PER_SECOND,
        suggested_unit_of_measurement=UnitOfDataRate.MEGABITS_PER_SECOND,
        suggested_display_precision=0,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    FritzSensorDescription(
        key="max_upload_rate",
        section="wan",
        value_fn=_get("max_up"),
        device_class=SensorDeviceClass.DATA_RATE,
        native_unit_of_measurement=UnitOfDataRate.BITS_PER_SECOND,
        suggested_unit_of_measurement=UnitOfDataRate.MEGABITS_PER_SECOND,
        suggested_display_precision=0,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    FritzSensorDescription(
        key="bytes_received",
        section="wan",
        value_fn=_get("bytes_received"),
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        suggested_unit_of_measurement=UnitOfInformation.GIGABYTES,
        suggested_display_precision=1,
    ),
    FritzSensorDescription(
        key="bytes_sent",
        section="wan",
        value_fn=_get("bytes_sent"),
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        suggested_unit_of_measurement=UnitOfInformation.GIGABYTES,
        suggested_display_precision=1,
    ),
    FritzSensorDescription(
        key="last_connection_error",
        section="wan",
        value_fn=_get("last_error"),
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    FritzSensorDescription(
        key="wlan_clients",
        section="wlan",
        value_fn=_get("clients_total"),
        state_class=SensorStateClass.MEASUREMENT,
    ),
    FritzSensorDescription(
        key="known_devices",
        section="lan",
        value_fn=_get("hosts_total"),
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    FritzSensorDescription(
        key="dsl_noise_margin_down",
        section="dsl",
        value_fn=_get("noise_margin_down"),
        native_unit_of_measurement="dB",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        require_value=True,
    ),
    FritzSensorDescription(
        key="dsl_noise_margin_up",
        section="dsl",
        value_fn=_get("noise_margin_up"),
        native_unit_of_measurement="dB",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        require_value=True,
    ),
    FritzSensorDescription(
        key="dsl_attenuation_down",
        section="dsl",
        value_fn=_get("attenuation_down"),
        native_unit_of_measurement="dB",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        require_value=True,
    ),
    FritzSensorDescription(
        key="dsl_attenuation_up",
        section="dsl",
        value_fn=_get("attenuation_up"),
        native_unit_of_measurement="dB",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        require_value=True,
    ),
    FritzSensorDescription(
        key="cpu_temperature",
        section="system",
        value_fn=_get("cpu_temperature"),
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_category=EntityCategory.DIAGNOSTIC,
        require_value=True,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: FritzConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Sensoren anlegen. DSL- und CPU-Werte nur, wenn die Box sie liefert."""
    manager = entry.runtime_data
    data = manager.data or {}
    entities = []
    for description in SENSORS:
        section = data.get(description.section) or {}
        if description.require_value and description.value_fn(section) is None:
            continue
        entities.append(FritzSensor(manager, description))
    async_add_entities(entities)


class FritzSensor(FritzEntity, SensorEntity):
    """Ein Sensor aus den Daten der FRITZ!Box."""

    entity_description: FritzSensorDescription

    def __init__(self, manager, description: FritzSensorDescription) -> None:
        super().__init__(manager, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> Any:
        return self.entity_description.value_fn(self._section(self.entity_description.section))
