"""Medidor de drift: ¿el precio se mueve de forma predecible TRAS una noticia?

Esta es la pregunta del millón del experimento. Para cada noticia guardada:
  - miramos el precio en el momento de la noticia,
  - y el precio 1h / 4h / 24h después,
  - y el retorno entre ambos.

Luego agrupamos por el sentimiento de la noticia. La hipótesis a falsar:
  "las noticias POSITIVAS van seguidas de drift al alza, y las NEGATIVAS de
   drift a la baja, MÁS de lo que ocurriría al azar".

Si los grupos positivo y negativo no se separan, no hay señal explotable. Lo
honesto es que muy probablemente no la haya con pocos datos: esto necesita
semanas de recolección para decir algo serio.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass

import pandas as pd

from src import exchange as ex
from src.news.store import CSV_PATH

HORIZONTES_H = [1, 4, 24]
UMBRAL_POS = 0.3   # compound por encima -> noticia positiva
UMBRAL_NEG = -0.3  # compound por debajo -> noticia negativa


@dataclass
class FilaEvento:
    activo: str
    ts: int
    sentimiento: float


def _cargar_eventos() -> list[FilaEvento]:
    if not CSV_PATH.exists():
        return []
    eventos: list[FilaEvento] = []
    with open(CSV_PATH, "r", encoding="utf-8", newline="") as f:
        for fila in csv.DictReader(f):
            activos = fila["activos"].strip()
            if not activos:
                continue
            ts = int(fila["ts_publicado"])
            sent = float(fila["sentimiento"])
            # Una noticia puede mencionar varios activos: una fila por activo.
            for a in activos.split(","):
                eventos.append(FilaEvento(activo=a, ts=ts, sentimiento=sent))
    eventos.sort(key=lambda e: e.ts)
    return eventos


def _serie_precios(bolsa, activo: str, desde_ts: int, hasta_ts: int):
    """Serie de cierres (indexada por epoch s) para un activo, en 5m."""
    symbol = f"{activo}/USDT"
    ms_margen = 6 * 3600 * 1000
    desde_ms = desde_ts * 1000 - ms_margen
    velas = []
    cursor = desde_ms
    fin_ms = hasta_ts * 1000 + ms_margen
    while cursor < fin_ms:
        lote = bolsa.fetch_ohlcv(symbol, "5m", since=cursor, limit=1000)
        if not lote:
            break
        velas.extend(lote)
        cursor = lote[-1][0] + 5 * 60 * 1000
        if len(lote) < 1000:
            break
    if not velas:
        return None
    s = pd.Series(
        {int(v[0] / 1000): float(v[4]) for v in velas}
    ).sort_index()
    return s


def _precio_en(serie: pd.Series, ts: int):
    """Último cierre conocido en o antes de ts (lo que sabríamos en tiempo real)."""
    previos = serie.loc[:ts]
    return float(previos.iloc[-1]) if len(previos) else None


def medir() -> dict:
    import time

    eventos = _cargar_eventos()
    ahora = int(time.time())
    bolsa = ex.crear_exchange_datos()

    # Resultados: {horizonte: {"pos": [retornos], "neg": [...], "neu": [...]}}
    res = {h: {"pos": [], "neg": [], "neu": []} for h in HORIZONTES_H}

    # Cacheamos la serie de precios por activo para no descargar mil veces.
    series: dict[str, pd.Series] = {}
    activos = sorted({e.activo for e in eventos})
    if not eventos:
        return {"eventos": 0, "res": res, "medibles": 0}

    ts_min = min(e.ts for e in eventos)
    for a in activos:
        try:
            s = _serie_precios(bolsa, a, ts_min, ahora)
            if s is not None:
                series[a] = s
        except Exception:  # noqa: BLE001
            continue

    medibles = 0
    for e in eventos:
        s = series.get(e.activo)
        if s is None:
            continue
        p0 = _precio_en(s, e.ts)
        if not p0:
            continue
        grupo = "pos" if e.sentimiento >= UMBRAL_POS else "neg" if e.sentimiento <= UMBRAL_NEG else "neu"
        for h in HORIZONTES_H:
            t_fut = e.ts + h * 3600
            if t_fut > ahora:
                continue  # aún no ha pasado ese tiempo
            p1 = _precio_en(s, t_fut)
            if not p1:
                continue
            res[h][grupo].append((p1 - p0) / p0)
            medibles += 1

    return {"eventos": len(eventos), "res": res, "medibles": medibles}
