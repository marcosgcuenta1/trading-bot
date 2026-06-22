"""Recolector: lee los feeds RSS, analiza cada noticia y la guarda.

No filtra por activo aquí: guarda todo (incluso noticias sin cripto detectada),
porque para el experimento queremos también saber cuántas noticias son ruido.
"""
from __future__ import annotations

import time
from calendar import timegm

import feedparser

from src.news import sentiment, store
from src.news.sources import FEEDS_RSS


def _ts_publicado(entry) -> int:
    """Epoch en segundos de la fecha de publicación; ahora mismo si no la trae."""
    t = getattr(entry, "published_parsed", None) or getattr(entry, "updated_parsed", None)
    return timegm(t) if t else int(time.time())


def recolectar() -> dict:
    """Lee todos los feeds una vez. Devuelve un pequeño resumen de lo recogido."""
    eventos: list[store.Evento] = []
    por_fuente: dict[str, int] = {}

    for nombre, url in FEEDS_RSS:
        try:
            feed = feedparser.parse(url)
        except Exception:  # noqa: BLE001
            por_fuente[nombre] = -1  # marca de fallo
            continue

        por_fuente[nombre] = len(feed.entries)
        for entry in feed.entries:
            titulo = getattr(entry, "title", "")
            resumen = getattr(entry, "summary", "")
            enlace = getattr(entry, "link", "")
            if not enlace:
                continue

            ana = sentiment.analizar(f"{titulo}. {resumen}")
            eventos.append(
                store.Evento(
                    fuente=nombre,
                    titulo=titulo,
                    url=enlace,
                    ts_publicado=_ts_publicado(entry),
                    activos=ana.activos,
                    sentimiento=ana.sentimiento,
                )
            )

    nuevos = store.guardar(eventos)
    con_activo = [e for e in eventos if e.activos]
    return {
        "leidos": len(eventos),
        "nuevos": nuevos,
        "con_cripto_detectada": len(con_activo),
        "por_fuente": por_fuente,
        "muestra": sorted(con_activo, key=lambda e: abs(e.sentimiento), reverse=True)[:8],
    }
