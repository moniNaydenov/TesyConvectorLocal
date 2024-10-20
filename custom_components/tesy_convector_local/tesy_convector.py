import aiohttp
import async_timeout
import logging

_LOGGER = logging.getLogger(__name__)

class TesyConvector:
    def __init__(self, ip_address):
        self.base_url = f"http://{ip_address}"

    async def send_command(self, endpoint, payload):
        url = f"{self.base_url}/{endpoint}"

        async with aiohttp.ClientSession() as session:
            try:
                async with async_timeout.timeout(10):
                    async with session.post(url, json=payload) as response:
                        try:
                            # Try to parse the response as JSON even if the Content-Type is incorrect
                            return await response.json(content_type=None)
                        except aiohttp.ContentTypeError:
                            # If parsing fails, log the plain text response
                            text_response = await response.text()
                            _LOGGER.error("Unexpected response format: %s", text_response)
                            return {"error": f"Unexpected response: {text_response}"}
            except aiohttp.ClientError as e:
                _LOGGER.error("HTTP error communicating with Tesy Convector: %s", e)
                return {"error": str(e)}
            except Exception as e:
                _LOGGER.error("Error communicating with Tesy Convector: %s", e)
                return {"error": str(e)}

    def get_status(self):
        return self.send_command("getStatus", {})

    def turn_on(self):
        return self.send_command("onOff", {"status": "on"})

    def turn_off(self):
        return self.send_command("onOff", {"status": "off"})

    def set_mode(self, mode):
        # Mode could be: off, eco, comfort, etc.
        return self.send_command("setMode", {"name": mode})

    def set_temperature(self, temp):
        return self.send_command("setTemp", {"temp": temp})

    def set_adaptive_start(self, status):
        # Status: on or off
        return self.send_command("setAdaptiveStart", {"status": status})

    def set_opened_window(self, status):
        # Status: on or off
        return self.send_command("setOpenedWindow", {"status": status})

    def set_delayed_start(self, time, temp):
        # Time in minutes and temperature
        return self.send_command("setDelayedStart", {"status": "on", "time": time, "temp": temp})

    def set_temperature_correction(self, temp):
        # Temperature correction
        return self.send_command("setTCorrection", {"temp": temp})

    def set_anti_frost(self, status):
        # Status: on or off
        return self.send_command("setAntiFrost", {"status": status})

    def set_comfort_temperature(self, temp):
        return self.send_command("setComfortTemp", {"temp": temp})

    def set_eco_temperature(self, temp, time):
        # Time in minutes
        return self.send_command("setEcoTemp", {"temp": temp, "time": time})

    def set_sleep_temperature(self, temp, time):
        # Time in minutes
        return self.send_command("setSleepTemp", {"temp": temp, "time": time})

    def set_uv(self, status):
        # Status: on or off
        return self.send_command("setUV", {"status": status})

    def lock_device(self, status):
        # Status: on or off
        return self.send_command("setLockDevice", {"status": status})