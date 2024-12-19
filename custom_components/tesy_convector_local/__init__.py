from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .climate import async_setup_entry
from .const import DOMAIN


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Tesy Convector component."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Tesy Convector from a config entry."""
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(entry, ["climate"])
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    return await hass.config_entries.async_forward_entry_unload(entry, "climate")