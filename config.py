"""Configuración central del bot.

Lee las variables del archivo .env (que NO se sube a git) y las expone
como constantes para el resto del proyecto. Un único punto de verdad.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Carga el .env que esté junto a este archivo
ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")


def _as_bool(value: str | None, default: bool = True) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "si", "sí"}


# --- Exchange / credenciales -------------------------------------------------
EXCHANGE: str = os.getenv("EXCHANGE", "binance").strip().lower()
TESTNET: bool = _as_bool(os.getenv("TESTNET"), default=True)
API_KEY: str = os.getenv("API_KEY", "").strip()
API_SECRET: str = os.getenv("API_SECRET", "").strip()

# --- Parámetros de mercado ---------------------------------------------------
SYMBOL: str = os.getenv("SYMBOL", "BTC/USDT").strip()
TIMEFRAME: str = os.getenv("TIMEFRAME", "5m").strip()

# --- Rutas -------------------------------------------------------------------
LOGS_DIR = ROOT / "logs"
DATA_DIR = ROOT / "data"


def tiene_credenciales() -> bool:
    """¿Hay claves configuradas? (necesarias para saldo y órdenes)."""
    return bool(API_KEY and API_SECRET and not API_KEY.startswith("pega_aqui"))
