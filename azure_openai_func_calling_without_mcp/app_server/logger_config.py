import logging
import os

log_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(log_dir, "server_logs.log")

logger = logging.getLogger("server_logger")
logger.setLevel(logging.INFO)

if not logger.hasHandlers():
    file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
    formatter = logging.Formatter(
        fmt="%(asctime)s — %(levelname)s — %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
