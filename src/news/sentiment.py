"""Análisis de una noticia: ¿de qué cripto habla y con qué tono?

Dos tareas:
  1. Detectar qué activos menciona (por palabras clave / tickers).
  2. Puntuar el sentimiento (positivo / negativo) con VADER, un analizador
     ligero basado en lexicón (sin modelos pesados, va sobrado en cualquier PC).

VADER está pensado para inglés de redes sociales, no para finanzas; por eso le
añadimos un pequeño lexicón cripto (hack, ban, ETF, partnership...) para que
capte el tono del sector. Es un punto de partida, no la verdad absoluta.
"""
from __future__ import annotations

from dataclasses import dataclass

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Activo -> palabras clave que lo mencionan (en minúsculas).
ACTIVOS: dict[str, list[str]] = {
    "BTC": ["bitcoin", "btc", "satoshi"],
    "ETH": ["ethereum", "ether", "eth ", "vitalik"],
    "SOL": ["solana", "sol "],
    "XRP": ["xrp", "ripple"],
    "BNB": ["binance coin", "bnb"],
    "DOGE": ["dogecoin", "doge"],
    "ADA": ["cardano", "ada "],
    "AVAX": ["avalanche", "avax"],
    "LINK": ["chainlink", "link "],
    "MATIC": ["polygon", "matic"],
}

# Términos del argot cripto que VADER no conoce. Valencia de -4 (muy malo) a +4.
LEXICO_CRIPTO: dict[str, float] = {
    "hack": -3.0, "hacked": -3.0, "exploit": -3.0, "breach": -2.5,
    "scam": -3.0, "rug": -3.0, "rugpull": -3.5, "fraud": -3.0,
    "ban": -2.5, "banned": -2.5, "lawsuit": -2.0, "sued": -2.0,
    "crackdown": -2.0, "delist": -2.0, "delisted": -2.0, "halt": -1.5,
    "etf": 1.5, "approval": 2.5, "approved": 2.5, "partnership": 2.5,
    "adoption": 2.0, "integration": 1.5, "upgrade": 1.5, "listing": 2.0,
    "bullish": 3.0, "bearish": -3.0, "surge": 2.0, "rally": 2.0,
    "soar": 2.5, "plunge": -2.5, "crash": -3.0, "dump": -2.0, "pump": 1.0,
}

_analizador = SentimentIntensityAnalyzer()
_analizador.lexicon.update(LEXICO_CRIPTO)


@dataclass
class Analisis:
    activos: list[str]
    sentimiento: float  # compound de VADER, de -1 (muy negativo) a +1 (muy positivo)


def analizar(texto: str) -> Analisis:
    t = texto.lower()
    activos = [sym for sym, claves in ACTIVOS.items() if any(c in t for c in claves)]
    score = _analizador.polarity_scores(texto)["compound"]
    return Analisis(activos=activos, sentimiento=score)
