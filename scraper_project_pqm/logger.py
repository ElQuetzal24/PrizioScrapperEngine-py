from loguru import logger
import sys

logger.remove()  # Elimina el logger por defecto
logger.add(sys.stdout, colorize=True, format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <cyan>{message}</cyan>")
logger.add("logs/scraper.log", rotation="1 MB", retention="7 days", compression="zip")
