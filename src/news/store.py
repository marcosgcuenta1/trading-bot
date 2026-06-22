"""Almacén de eventos de noticias en CSV (append-only, apto para git/GitHub Actions).

¿Por qué CSV y no SQLite? Porque el recolector vivirá en GitHub Actions, que
arranca limpio en cada ejecución. Persistimos los eventos en un CSV dentro del
repo: cada ejecución AÑADE las noticias nuevas y hace commit. Git versiona texto
de maravilla (diffs legibles, sin los conflictos binarios de SQLite).

Guardamos cada noticia una sola vez (dedupe por URL) con DOS tiempos:
  - ts_publicado: cuándo dice la fuente que se publicó.
  - ts_recogido:  cuándo la vimos nosotros (mide nuestra latencia real).
"""
from __future__ import annotations

import csv
import time
from dataclasses import dataclass

import config

CSV_PATH = config.DATA_DIR / "news.csv"
CAMPOS = ["fuente", "titulo", "url", "ts_publicado", "ts_recogido", "activos", "sentimiento"]


@dataclass
class Evento:
    fuente: str
    titulo: str
    url: str
    ts_publicado: int  # epoch en segundos
    activos: list[str]
    sentimiento: float


def _urls_existentes() -> set[str]:
    if not CSV_PATH.exists():
        return set()
    with open(CSV_PATH, "r", encoding="utf-8", newline="") as f:
        return {fila["url"] for fila in csv.DictReader(f)}


def guardar(eventos: list[Evento]) -> int:
    """Añade al CSV solo los eventos cuya URL no estuviera ya. Devuelve cuántos."""
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    vistas = _urls_existentes()
    ahora = int(time.time())
    nuevos = [e for e in eventos if e.url and e.url not in vistas]
    if not nuevos:
        return 0

    escribir_cabecera = not CSV_PATH.exists()
    with open(CSV_PATH, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        if escribir_cabecera:
            w.writeheader()
        for e in nuevos:
            w.writerow(
                {
                    "fuente": e.fuente,
                    "titulo": e.titulo,
                    "url": e.url,
                    "ts_publicado": e.ts_publicado,
                    "ts_recogido": ahora,
                    "activos": ",".join(e.activos),
                    "sentimiento": f"{e.sentimiento:.4f}",
                }
            )
    return len(nuevos)


def total() -> int:
    if not CSV_PATH.exists():
        return 0
    with open(CSV_PATH, "r", encoding="utf-8", newline="") as f:
        return sum(1 for _ in csv.DictReader(f))
