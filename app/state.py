import asyncio
from paho.mqtt import client 

mqtt_client: client.Client | None = None
pending_key: str | None = None
active_key: str | None = None
connection_event: asyncio.Event = asyncio.Event()
connection_accepted: bool = False