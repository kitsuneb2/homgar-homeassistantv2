"""Support for HomGar sensors."""
from __future__ import annotations

import logging
from dataclasses import replace
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfLength,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import HomgarConfigEntry
from .const import (
    ICON_TEMPERATURE,
    ICON_HUMIDITY,
    ICON_PRESSURE,
    ICON_SOIL_MOISTURE,
    ICON_ZONE_STATUS,
    ICON_AIR_SENSOR,
    ICON_RAIN_SENSOR,
    ICON_RAINFALL,
)
from .coordinator import HomgarDataUpdateCoordinator
from .devices import (
    RainPointDisplayHub,
    RainPointSoilMoistureSensor,
    RainPointAirSensor,
    RainPointRainSensor,
    HTV405FRF,
)
from .entity import HomgarEntity

_LOGGER = logging.getLogger(__name__)

# Base sensor descriptions
SENSOR_DESCRIPTIONS = {
    "temperature": SensorEntityDescription(
        key="temperature",
        name="Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        icon=ICON_TEMPERATURE,
    ),
    "humidity": SensorEntityDescription(
        key="humidity",
        name="Humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon=ICON_HUMIDITY,
    ),
    "pressure": SensorEntityDescription(
        key="pressure",
        name="Pressure",
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=UnitOfPressure.PA,
        state_class=SensorStateClass.MEASUREMENT,
        icon=ICON_PRESSURE,
    ),
    "soil_moisture": SensorEntityDescription(
        key="soil_moisture",
        name="Soil Moisture",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon=ICON_SOIL_MOISTURE,
    ),
    "rainfall": SensorEntityDescription(
        key="rainfall",
        name="Rainfall",
        device_class=SensorDeviceClass.PRECIPITATION,
        native_unit_of_measurement=UnitOfLength.MILLIMETERS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon=ICON_RAINFALL,
    ),
    "zone_status": SensorEntityDescription(
        key="zone_status",
        name="Zone Status",
        icon=ICON_ZONE_STATUS,
    ),
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: HomgarConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HomGar sensors from a config entry."""
    coordinator = config_entry.runtime_data
    _LOGGER.info("[DEBUG] [Sensor Setup] Initializing sensors for %d devices", len(coordinator.devices))

    entities = []

    for device_id, device in coordinator.devices.items():
        if isinstance(device, RainPointDisplayHub):
            entities.extend([
                HomgarTemperatureSensor(coordinator, device_id, device),
                HomgarHumiditySensor(coordinator, device_id, device),
                HomgarPressureSensor(coordinator, device_id, device),
            ])
        elif isinstance(device, RainPointSoilMoistureSensor):
            entities.extend([
                HomgarSoilMoistureSensor(coordinator, device_id, device),
                HomgarSoilTemperatureSensor(coordinator, device_id, device),
            ])
        elif isinstance(device, RainPointAirSensor):
            entities.extend([
                HomgarAirTemperatureSensor(coordinator, device_id, device),
                HomgarAirHumiditySensor(coordinator, device_id, device),
            ])
        elif isinstance(device, RainPointRainSensor):
            entities.append(HomgarRainfallSensor(coordinator, device_id, device))
        elif isinstance(device, HTV405FRF):
            for zone in [1, 2, 3, 4]:
                entities.append(
                    HomgarZoneStatusSensor(coordinator, device_id, device, zone)
                )

    _LOGGER.info("[DEBUG] [Sensor Setup] Adding %d sensor entities to HA", len(entities))
    async_add_entities(entities)


class HomgarSensor(HomgarEntity, SensorEntity):
    """Base class for all HomGar sensors."""

    def __init__(
        self,
        coordinator: HomgarDataUpdateCoordinator,
        device_id: str,
        device: Any,
        description: SensorEntityDescription,
        zone: int | None = None,
    ) -> None:
        """Initialize the base sensor."""
        super().__init__(coordinator, device_id, device)
        self.entity_description = description
        self.zone = zone
        
        if zone is not None:
            self._attr_name = f"{device.name} Zone {zone} {description.name}"
            self._attr_unique_id = f"{device.mid}_{device.address}_zone_{zone}_{description.key}"
        else:
            self._attr_name = f"{device.name} {description.name}"
            self._attr_unique_id = f"{device.mid}_{device.address}_{description.key}"


class HomgarTemperatureSensor(HomgarSensor):
    """Ambient temperature sensor."""
    def __init__(self, coordinator, device_id, device):
        super().__init__(coordinator, device_id, device, SENSOR_DESCRIPTIONS["temperature"])

    @property
    def native_value(self) -> float | None:
        if self.device and hasattr(self.device, 'temp_mk_current') and self.device.temp_mk_current:
            return round(self.device.temp_mk_current * 1e-3 - 273.15, 1)
        return None


class HomgarHumiditySensor(HomgarSensor):
    """Ambient humidity sensor."""
    def __init__(self, coordinator, device_id, device):
        super().__init__(coordinator, device_id, device, SENSOR_DESCRIPTIONS["humidity"])

    @property
    def native_value(self) -> int | None:
        return getattr(self.device, 'hum_current', None)


class HomgarPressureSensor(HomgarSensor):
    """Atmospheric pressure sensor."""
    def __init__(self, coordinator, device_id, device):
        super().__init__(coordinator, device_id, device, SENSOR_DESCRIPTIONS["pressure"])

    @property
    def native_value(self) -> int | None:
        return getattr(self.device, 'press_pa_current', None)


class HomgarSoilMoistureSensor(HomgarSensor):
    """Soil moisture sensor."""
    def __init__(self, coordinator, device_id, device):
        super().__init__(coordinator, device_id, device, SENSOR_DESCRIPTIONS["soil_moisture"])

    @property
    def native_value(self) -> int | None:
        return getattr(self.device, 'moist_percent_current', None)


class HomgarSoilTemperatureSensor(HomgarSensor):
    """Soil temperature sensor."""
    def __init__(self, coordinator, device_id, device):
        super().__init__(coordinator, device_id, device, SENSOR_DESCRIPTIONS["temperature"])

    @property
    def native_value(self) -> float | None:
        if self.device and hasattr(self.device, 'temp_mk_current') and self.device.temp_mk_current:
            return round(self.device.temp_mk_current * 1e-3 - 273.15, 1)
        return None


class HomgarAirTemperatureSensor(HomgarSensor):
    """Air temperature sensor with weather icon fix."""
    def __init__(self, coordinator, device_id, device):
        # FIX: Use replace() for frozen dataclass
        new_desc = replace(SENSOR_DESCRIPTIONS["temperature"], icon=ICON_AIR_SENSOR)
        super().__init__(coordinator, device_id, device, new_desc)

    @property
    def native_value(self) -> float | None:
        if self.device and hasattr(self.device, 'temp_mk_current') and self.device.temp_mk_current:
            return round(self.device.temp_mk_current * 1e-3 - 273.15, 1)
        return None


class HomgarAirHumiditySensor(HomgarSensor):
    """Air humidity sensor with weather icon fix."""
    def __init__(self, coordinator, device_id, device):
        # FIX: Use replace() for frozen dataclass
        new_desc = replace(SENSOR_DESCRIPTIONS["humidity"], icon=ICON_AIR_SENSOR)
        super().__init__(coordinator, device_id, device, new_desc)

    @property
    def native_value(self) -> int | None:
        return getattr(self.device, 'hum_current', None)


class HomgarRainfallSensor(HomgarSensor):
    """Rainfall sensor."""
    def __init__(self, coordinator, device_id, device):
        super().__init__(coordinator, device_id, device, SENSOR_DESCRIPTIONS["rainfall"])

    @property
    def native_value(self) -> float | None:
        return getattr(self.device, 'rainfall_current', None)


class HomgarZoneStatusSensor(HomgarSensor):
    """Status sensor (On/Off/Idle) for irrigation zones."""
    def __init__(self, coordinator, device_id, device, zone):
        super().__init__(coordinator, device_id, device, SENSOR_DESCRIPTIONS["zone_status"], zone)

    @property
    def native_value(self) -> str | None:
        if self.device and hasattr(self.device, 'get_zone_status_text'):
            return self.device.get_zone_status_text(self.zone)
        return None