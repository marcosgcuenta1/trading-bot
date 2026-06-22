"""Capa de conexión al exchange mediante ccxt.

Usar ccxt (en vez de python-binance) es deliberado: el día que pasemos a real
en un exchange regulado por MiCA (Kraken, Coinbase...), cambiamos EXCHANGE en el
.env y el resto del código sigue igual. La lógica de la estrategia no se entera.
"""
from __future__ import annotations

import ccxt

import config


def crear_exchange() -> ccxt.Exchange:
    """Devuelve una instancia de ccxt configurada según el .env.

    Si TESTNET=True, activa el modo sandbox (dinero ficticio).
    """
    clase = getattr(ccxt, config.EXCHANGE)
    exchange = clase(
        {
            "apiKey": config.API_KEY,
            "secret": config.API_SECRET,
            "enableRateLimit": True,  # respeta los límites del exchange automáticamente
            "options": {"defaultType": "spot"},
        }
    )

    if config.TESTNET:
        # Apunta a los servidores de pruebas en vez de a los reales.
        exchange.set_sandbox_mode(True)

    return exchange


def crear_exchange_datos() -> ccxt.Exchange:
    """Exchange SOLO para descargar histórico real de mercado (mainnet pública).

    Para backtesting queremos los precios reales del mercado, no el libro de la
    testnet (que es artificial). Estos endpoints son públicos: no usan claves.
    """
    clase = getattr(ccxt, config.EXCHANGE)
    return clase({"enableRateLimit": True, "options": {"defaultType": "spot"}})


def descargar_historico(
    exchange: ccxt.Exchange,
    symbol: str,
    timeframe: str,
    velas_totales: int = 5000,
):
    """Descarga muchas velas paginando hacia atrás (el límite por llamada es ~1000).

    Devuelve una lista de [timestamp, open, high, low, close, volume] ordenada.
    """
    por_llamada = 1000
    ms_por_vela = exchange.parse_timeframe(timeframe) * 1000
    ahora = exchange.milliseconds()
    desde = ahora - velas_totales * ms_por_vela

    todas: list = []
    while desde < ahora:
        lote = exchange.fetch_ohlcv(symbol, timeframe, since=desde, limit=por_llamada)
        if not lote:
            break
        todas.extend(lote)
        desde = lote[-1][0] + ms_por_vela
        if len(lote) < por_llamada:
            break

    # Quita duplicados por timestamp, por si los lotes solapan.
    vistos = {}
    for v in todas:
        vistos[v[0]] = v
    return [vistos[t] for t in sorted(vistos)]


def precio_actual(exchange: ccxt.Exchange, symbol: str) -> float:
    """Último precio negociado de un par. Endpoint público: no necesita claves."""
    ticker = exchange.fetch_ticker(symbol)
    return float(ticker["last"])


def velas(exchange: ccxt.Exchange, symbol: str, timeframe: str, limite: int = 200):
    """Velas OHLCV (open, high, low, close, volume). Endpoint público.

    Devuelve una lista de [timestamp, open, high, low, close, volume].
    """
    return exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limite)


def saldo(exchange: ccxt.Exchange) -> dict:
    """Saldo de la cuenta. Endpoint privado: necesita claves API."""
    return exchange.fetch_balance()
