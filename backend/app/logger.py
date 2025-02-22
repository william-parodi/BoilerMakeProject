import logging

logger = logging.getLogger("pizza_app")
logger.setLevel(logging.DEBUG)  # Adjust the level as appropriate for your environment

handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
