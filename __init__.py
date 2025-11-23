"""The Flux Node Monitor integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .flux_api import FluxMonitor

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]
DOMAIN = "flux_monitor"

SCAN_INTERVAL = timedelta(minutes=5)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Flux Monitor from a config entry."""
    wallet_address = entry.data["wallet_address"]
    node_ips = entry.data.get("node_ips", "").split(",")
    node_ips = [ip.strip() for ip in node_ips if ip.strip()]

    monitor = FluxMonitor(wallet_address, node_ips)

    async def async_update_data():
        """Fetch data from API."""
        try:
            return await monitor.get_all_data()
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=async_update_data,
        update_interval=SCAN_INTERVAL,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "monitor": monitor,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        monitor = hass.data[DOMAIN][entry.entry_id]["monitor"]
        await monitor.close()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
