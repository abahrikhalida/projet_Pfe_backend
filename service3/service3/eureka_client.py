import asyncio
from threading import Thread
from decouple import config
from py_eureka_client.eureka_client import EurekaClient

def start_eureka_client():
    EUREKA_SERVER = config("EUREKA_SERVER")
    EUREKA_APP_NAME = config("EUREKA_APP_NAME")
    EUREKA_HOST = config("EUREKA_HOST")
    EUREKA_PORT = int(config("EUREKA_PORT"))

    async def start_client():
        client = EurekaClient(
            eureka_server=EUREKA_SERVER,
            app_name=EUREKA_APP_NAME,
            instance_host=EUREKA_HOST,
            instance_port=EUREKA_PORT,
        )
        await client.start()

    # Run in a separate thread to avoid blocking Django startup
    Thread(target=lambda: asyncio.run(start_client()), daemon=True).start()