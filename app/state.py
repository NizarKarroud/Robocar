import asyncio

pending_key: str | None = None
active_key: str | None = None
connection_event: asyncio.Event = asyncio.Event()
connection_accepted: bool = False