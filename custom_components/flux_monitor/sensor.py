"""Support for Flux Monitor sensors."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
    SensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Flux Monitor sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    
    sensors = []
    
    # Sensors pour chaque node
    if coordinator.data and "nodes" in coordinator.data:
        for idx, node_data in enumerate(coordinator.data["nodes"]):
            node_ip = node_data.get("ip_port", f"node_{idx}")
            
            # Sensors individuels pour chaque node
            sensors.extend([
                FluxNodeSensor(coordinator, entry, idx, "next_payment", "Next Payment", None),
                FluxNodeSensor(coordinator, entry, idx, "rank", "Rank", None),
                FluxNodeSensor(coordinator, entry, idx, "tier", "Tier", None),
                FluxNodeSensor(coordinator, entry, idx, "ip_port", "IP:Port", None),
                FluxNodeSensor(coordinator, entry, idx, "flux_os_version", "FluxOS Version", None),
                FluxNodeSensor(coordinator, entry, idx, "benchmark_version", "Benchmark Version", None),
                FluxNodeSensor(coordinator, entry, idx, "eps", "EPS", None),
                FluxNodeSensor(coordinator, entry, idx, "dws", "DWS", "MB/s"),
                FluxNodeSensor(coordinator, entry, idx, "download", "Download", "Mbps"),
                FluxNodeSensor(coordinator, entry, idx, "upload", "Upload", "Mbps"),
                FluxNodeSensor(coordinator, entry, idx, "last_benchmark", "Last Benchmark", None),
                FluxNodeSensor(coordinator, entry, idx, "uptime", "Uptime", "s"),
                FluxNodeSensor(coordinator, entry, idx, "score", "Score", None),
                FluxNodeSensor(coordinator, entry, idx, "apps", "Apps Count", None),
                FluxNodeSensor(coordinator, entry, idx, "blocks_until_payment", "Blocks Until Payment", "blocks"),
            ])
    
    # Sensors pour le wallet
    sensors.extend([
        FluxWalletSensor(coordinator, entry, "balance_flux", "Balance", "FLUX"),
        FluxWalletSensor(coordinator, entry, "balance_eur", "Balance EUR", "EUR"),
        FluxWalletSensor(coordinator, entry, "monthly_flux", "Monthly Rewards", "FLUX"),
        FluxWalletSensor(coordinator, entry, "monthly_eur", "Monthly Rewards EUR", "EUR"),
        FluxWalletSensor(coordinator, entry, "flux_price_eur", "FLUX Price", "EUR"),
    ])
    
    # Sensors pour les Parallel Assets
    sensors.extend([
        FluxParallelAssetSensor(coordinator, entry, "total_assets", "Total Assets", None),
        FluxParallelAssetSensor(coordinator, entry, "total_value", "Total Value", None),
    ])
    
    # Sensors pour l'écosystème
    sensors.extend([
        FluxEcosystemSensor(coordinator, entry, "cumulus", "Cumulus Nodes", "nodes"),
        FluxEcosystemSensor(coordinator, entry, "nimbus", "Nimbus Nodes", "nodes"),
        FluxEcosystemSensor(coordinator, entry, "stratus", "Stratus Nodes", "nodes"),
        FluxEcosystemSensor(coordinator, entry, "total", "Total Nodes", "nodes"),
    ])
    
    async_add_entities(sensors)


class FluxNodeSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Flux Node sensor."""

    def __init__(self, coordinator, config_entry, node_idx, sensor_key, sensor_name, unit):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._node_idx = node_idx
        self._sensor_key = sensor_key
        self._attr_name = f"Flux Node {node_idx + 1} {sensor_name}"
        self._attr_unique_id = f"{config_entry.entry_id}_node_{node_idx}_{sensor_key}"
        self._attr_native_unit_of_measurement = unit
        
        if sensor_key in ["balance_flux", "balance_eur", "monthly_flux", "monthly_eur"]:
            self._attr_state_class = SensorStateClass.TOTAL
        elif sensor_key in ["eps", "dws", "download", "upload", "uptime", "apps", "blocks_until_payment"]:
            self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data and "nodes" in self.coordinator.data:
            if self._node_idx < len(self.coordinator.data["nodes"]):
                node_data = self.coordinator.data["nodes"][self._node_idx]
                return node_data.get(self._sensor_key, "Unknown")
        return "Unknown"

    @property
    def extra_state_attributes(self):
        """Return extra attributes."""
        if self.coordinator.data and "nodes" in self.coordinator.data:
            if self._node_idx < len(self.coordinator.data["nodes"]):
                node_data = self.coordinator.data["nodes"][self._node_idx]
                
                attrs = {
                    "ip_port": node_data.get("ip_port", "N/A"),
                    "tier": node_data.get("tier", "N/A"),
                    "rank": node_data.get("rank", "N/A"),
                }
                
                # Ajoute la liste des apps si disponible
                if self._sensor_key == "apps" and "apps_list" in node_data:
                    attrs["apps_list"] = node_data["apps_list"]
                
                # Ajoute des infos de collateral
                if "collateral" in node_data:
                    attrs["collateral"] = node_data["collateral"]
                
                return attrs
        return {}


class FluxWalletSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Flux Wallet sensor."""

    def __init__(self, coordinator, config_entry, sensor_key, sensor_name, unit):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_key = sensor_key
        self._attr_name = f"Flux Wallet {sensor_name}"
        self._attr_unique_id = f"{config_entry.entry_id}_wallet_{sensor_key}"
        self._attr_native_unit_of_measurement = unit
        
        if sensor_key in ["balance_flux", "balance_eur", "monthly_flux", "monthly_eur"]:
            self._attr_state_class = SensorStateClass.TOTAL
        
        if unit == "EUR":
            self._attr_device_class = SensorDeviceClass.MONETARY

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data and "wallet" in self.coordinator.data:
            value = self.coordinator.data["wallet"].get(self._sensor_key, 0)
            if isinstance(value, float):
                return round(value, 2)
            return value
        return 0


class FluxParallelAssetSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Flux Parallel Asset sensor."""

    def __init__(self, coordinator, config_entry, sensor_key, sensor_name, unit):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_key = sensor_key
        self._attr_name = f"Flux {sensor_name}"
        self._attr_unique_id = f"{config_entry.entry_id}_pa_{sensor_key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data and "parallel_assets" in self.coordinator.data:
            return self.coordinator.data["parallel_assets"].get(self._sensor_key, 0)
        return 0

    @property
    def extra_state_attributes(self):
        """Return extra attributes."""
        if self.coordinator.data and "parallel_assets" in self.coordinator.data:
            pa_data = self.coordinator.data["parallel_assets"]
            if "assets_detail" in pa_data and self._sensor_key == "total_assets":
                return {"assets_detail": pa_data["assets_detail"]}
        return {}


class FluxEcosystemSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Flux Ecosystem sensor."""

    def __init__(self, coordinator, config_entry, sensor_key, sensor_name, unit):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_key = sensor_key
        self._attr_name = f"Flux Ecosystem {sensor_name}"
        self._attr_unique_id = f"{config_entry.entry_id}_eco_{sensor_key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data and "ecosystem" in self.coordinator.data:
            return self.coordinator.data["ecosystem"].get(self._sensor_key, 0)
        return 0

    @property
    def extra_state_attributes(self):
        """Return extra attributes."""
        if self.coordinator.data and "ecosystem" in self.coordinator.data:
            eco_data = self.coordinator.data["ecosystem"]
            if self._sensor_key == "total":
                return {
                    "cumulus": eco_data.get("cumulus", 0),
                    "nimbus": eco_data.get("nimbus", 0),
                    "stratus": eco_data.get("stratus", 0),
                }
        return {}
