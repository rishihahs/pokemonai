import asyncio
from pokemonai.smogon import controller

asyncio.get_event_loop().run_until_complete(controller.run())
