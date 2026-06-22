"""Estrategia trend-following (seguimiento de tendencia).

Idea, en una frase: operar a favor de la tendencia, no contra ella.

Reglas (solo largos/fuera; en spot no hay cortos):
  - ENTRAR (comprar) cuando la EMA rápida cruza POR ENCIMA de la EMA lenta
    Y el precio está por encima de la EMA de fondo (filtro de régimen alcista).
  - SALIR (vender) cuando la EMA rápida cruza POR DEBAJO de la EMA lenta.

El filtro de fondo es lo que separa una estrategia trend-following seria de un
simple cruce de medias: evita operar en mercados laterales, que es donde los
cruces de medias generan pérdidas por sobre-operar (whipsaw).

Esto NO es una recomendación de inversión; es un punto de partida medible que el
backtester va a juzgar con honestidad (con comisiones y slippage).
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class ParametrosEstrategia:
    ema_rapida: int = 20
    ema_lenta: int = 50
    ema_fondo: int = 200  # filtro de tendencia de fondo


def generar_senales(df: pd.DataFrame, params: ParametrosEstrategia) -> pd.DataFrame:
    """Añade columnas de indicadores y una columna 'posicion' (1 = comprado, 0 = fuera).

    Espera un DataFrame con columna 'close'. Devuelve el mismo DataFrame ampliado.
    """
    out = df.copy()
    out["ema_rapida"] = out["close"].ewm(span=params.ema_rapida, adjust=False).mean()
    out["ema_lenta"] = out["close"].ewm(span=params.ema_lenta, adjust=False).mean()
    out["ema_fondo"] = out["close"].ewm(span=params.ema_fondo, adjust=False).mean()

    # Condición de tendencia alcista: rápida sobre lenta y precio sobre el fondo.
    alcista = (out["ema_rapida"] > out["ema_lenta"]) & (out["close"] > out["ema_fondo"])

    # posicion = 1 mientras se cumpla la condición; 0 en caso contrario.
    out["posicion"] = alcista.astype(int)

    # Las primeras velas no tienen EMAs fiables: nos quedamos fuera.
    out.loc[: params.ema_fondo, "posicion"] = 0
    return out
