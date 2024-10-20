import asyncio

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVAC_MODE_OFF,
    HVAC_MODE_HEAT,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.components.climate import ClimateEntityFeature
from homeassistant.helpers.event import async_track_time_interval
from datetime import timedelta

from .tesy_convector import TesyConvector

import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Tesy Convector climate entity."""
    ip_address = config_entry.data.get("ip_address")
    temperature_entity = config_entry.data.get("temperature_entity")  # Get temperature entity if provided
    convector = TesyConvector(ip_address)
    async_add_entities([TesyConvectorClimate(convector, temperature_entity)])


class TesyConvectorClimate(ClimateEntity):
    """Representation of a Tesy Convector as a ClimateEntity."""

    def __init__(self, convector, temperature_entity=None):
        """Initialize the climate entity."""
        self.convector = convector
        self.temperature_entity = temperature_entity
        self._attr_name = "Tesy Convector"
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS  # Updated to use UnitOfTemperature.CELSIUS
        # Explicitly declare both TARGET_TEMPERATURE
        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.TURN_OFF | ClimateEntityFeature.TURN_ON
        )
        self._attr_hvac_modes = [HVAC_MODE_HEAT, HVAC_MODE_OFF]
        self._attr_min_temp = 10
        self._attr_max_temp = 30
        self._attr_target_temperature_step = 1
        self._hvac_mode = HVAC_MODE_OFF  # Default to off initially
        self._current_temp = None  # Variable to store current temperature
        self._target_temp = None  # Variable to store target temperature

    async def async_update(self):
        """Fetch new state data for this entity."""
        if self.temperature_entity:
            # Get the temperature from the specified entity
            temp_state = self.hass.states.get(self.temperature_entity)
            if temp_state:
                self._current_temp = float(temp_state.state)
        else:
            # Fallback to using the convector's temperature
            status = await self.convector.get_status()
            self._current_temp = status['payload']['setTemp']['payload']['temp']

        """Fetch new state data for this entity."""
        status = await self.convector.get_status()

        # Log the full response for debugging
        _LOGGER.debug("Tesy Convector status: %s", status)

        # Check if 'payload' exists before accessing it
        if 'payload' in status and 'onOff' in status['payload'] and 'status' in status['payload']['onOff']['payload']:
            self._hvac_mode = HVAC_MODE_HEAT if status['payload']['onOff']['payload']['status'] == 'on' else HVAC_MODE_OFF
            self._target_temp = status['payload']['setTemp']['payload']['temp']  # Set target temperature
        else:
            _LOGGER.error("Unexpected response structure from Tesy Convector: %s", status)
            # Optionally set default values in case of an unexpected structure
            self._hvac_mode = HVAC_MODE_OFF
            self._target_temp = None

    @property
    def hvac_mode(self):
        """Return the current HVAC mode."""
        return self._hvac_mode

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._current_temp

    @property
    def target_temperature(self):
        """Return the current target temperature."""
        return self._target_temp

    async def async_added_to_hass(self):
        """Run when entity is added to Home Assistant."""
        # Update the state every 20 seconds
        self._remove_update_listener = async_track_time_interval(
            self.hass, self.async_update, timedelta(seconds=10)
        )

    async def async_set_hvac_mode(self, hvac_mode):
        """Set the HVAC mode (on/off)."""
        if hvac_mode == HVAC_MODE_HEAT:
            await self.convector.turn_on()
        elif hvac_mode == HVAC_MODE_OFF:
            await self.convector.turn_off()

        # Add a delay after setting the HVAC mode to give the convector time to process
        await asyncio.sleep(0.1)

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        temp = kwargs.get("temperature")
        if temp is not None and self._target_temp != temp:
            await self.convector.set_temperature(temp)
            self._target_temp = temp  # Update the internal target temperature
            await asyncio.sleep(0.1)
