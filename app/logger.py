from __future__ import annotations
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from loguru import logger as _logger
from app.config import PROJECT_ROOT, Config

# Ensure logs directory exists so file sink creation never fails.
LOG_DIR: Path = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def setup_logger(config: Optional[Config] = None, name: str | None = None):
    """
    Configure loguru sinks based on an agent's Config.
    - Console sink: colorized, level from Config.log_level (default INFO).
    - File sink: logs/{name_or_timestamp}.log at same level.
    """
    cfg = config or Config()
    level = (getattr(cfg, "log_level", None) or "INFO").upper()

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    logfile_name = f"{name}_{timestamp}" if name else timestamp
    logfile_level = (getattr(cfg, "logfile_level", None) or "DEBUG").upper()

    _logger.remove()
    _logger.add(
        sys.stderr,
        level=level,
        colorize=True,
        enqueue=True,
        backtrace=True,
        diagnose=True,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
    )
    _logger.add(LOG_DIR / f"{logfile_name}.log", level=logfile_level, enqueue=True)
    return _logger


# Default logger for general use; agents can call setup_logger(agent.config, agent.name)
# to get per-agent levels and file prefixes.
logger = setup_logger()

# Testing the logger setup
if __name__ == "__main__":
    logger.info("Starting application")
    logger.debug("Debug message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")

    try:
        raise ValueError("Test error")
    except Exception as e:
        logger.exception(f"An error occurred: {e}")