# backend/app/utils/logger.py
"""Simple logger utility using Python's built‑in logging.
All modules can import ``logger`` and call ``logger.info`` etc.
"""

import logging
import sys

logger = logging.getLogger("campuseats")
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
