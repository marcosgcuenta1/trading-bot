"""Motor de backtest honesto.

"Honesto" significa tres cosas que la mayoría de backtests caseros se saltan y
por eso engañan a su autor:

  1. SIN look-ahead: operamos con la señal de la vela ANTERIOR (posicion.shift(1)).
     Nunca usamos información que no tendríamos en tiempo real.
  2. CON costes: cada operación paga comisión + slippage. En el corto plazo esto
     es lo que mata la mayoría de estrategias.
  3. CON benchmark: comparamos contra comprar y aguantar (buy & hold). Si la
     estrategia no bate a no hacer nada, no sirve, por bonita que sea la curva.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class Costes:
    comision_pct: float = 0.001   # 0,1 % por operación (taker típico en Binance)
    slippage_pct: float = 0.0005  # 0,05 % de deslizamiento estimado


@dataclass
class Resultado:
    velas: int
    dias: float
    retorno_estrategia: float
    retorno_buy_hold: float
    num_operaciones: int
    win_rate: float
    max_drawdown: float
    comisiones_pagadas_pct: float
    sharpe: float
    equity: pd.Series


def correr(df: pd.DataFrame, timeframe_min: float, costes: Costes) -> Resultado:
    """Ejecuta el backtest sobre un DataFrame que ya tiene columnas 'close' y 'posicion'."""
    d = df.copy()

    # Retorno del mercado vela a vela.
    d["ret_mercado"] = d["close"].pct_change().fillna(0.0)

    # Operamos con la señal de la vela anterior (evita look-ahead).
    pos = d["posicion"].shift(1).fillna(0)

    # Retorno bruto de la estrategia: solo capturamos mercado cuando estamos dentro.
    d["ret_estrategia"] = pos * d["ret_mercado"]

    # Coste: cada cambio de posición (entrar o salir) es una transacción.
    cambios = pos.diff().abs().fillna(0)
    coste_por_op = costes.comision_pct + costes.slippage_pct
    d["coste"] = cambios * coste_por_op
    d["ret_neto"] = d["ret_estrategia"] - d["coste"]

    # Curva de capital (equity), partiendo de 1.0.
    equity = (1 + d["ret_neto"]).cumprod()
    d["equity"] = equity

    # --- Métricas -----------------------------------------------------------
    retorno_estrategia = float(equity.iloc[-1] - 1)
    retorno_buy_hold = float((1 + d["ret_mercado"]).cumprod().iloc[-1] - 1)

    # Número de operaciones completas (una entrada = un trade).
    entradas = ((pos == 1) & (pos.shift(1) == 0)).sum()
    num_operaciones = int(entradas)

    # Win rate por operación: troceamos en tramos donde estuvimos dentro.
    win_rate = _win_rate_por_operacion(pos, d["ret_neto"])

    # Máximo drawdown sobre la curva de capital.
    pico = equity.cummax()
    drawdown = equity / pico - 1
    max_drawdown = float(drawdown.min())

    # Comisiones totales pagadas (en % sobre capital inicial).
    comisiones_pagadas = float(d["coste"].sum())

    # Sharpe anualizado (referencia, no dogma).
    velas_por_ano = (365 * 24 * 60) / timeframe_min
    media = d["ret_neto"].mean()
    desv = d["ret_neto"].std()
    sharpe = float(media / desv * math.sqrt(velas_por_ano)) if desv > 0 else 0.0

    dias = len(d) * timeframe_min / (60 * 24)

    return Resultado(
        velas=len(d),
        dias=dias,
        retorno_estrategia=retorno_estrategia,
        retorno_buy_hold=retorno_buy_hold,
        num_operaciones=num_operaciones,
        win_rate=win_rate,
        max_drawdown=max_drawdown,
        comisiones_pagadas_pct=comisiones_pagadas,
        sharpe=sharpe,
        equity=equity,
    )


def _win_rate_por_operacion(pos: pd.Series, ret_neto: pd.Series) -> float:
    """% de operaciones que cerraron en verde."""
    pnl_operaciones: list[float] = []
    dentro = False
    acum = 0.0
    for p, r in zip(pos.values, ret_neto.values):
        if p == 1:
            dentro = True
            acum += r
        elif dentro:  # acabamos de salir
            pnl_operaciones.append(acum)
            acum = 0.0
            dentro = False
    if dentro:
        pnl_operaciones.append(acum)

    if not pnl_operaciones:
        return 0.0
    ganadoras = sum(1 for x in pnl_operaciones if x > 0)
    return ganadoras / len(pnl_operaciones)
