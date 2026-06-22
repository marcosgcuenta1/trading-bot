"""Recoge noticias cripto una vez y muestra un resumen.

Ejecuta:   python scripts/collect_news.py

Para el experimento real, esto se ejecutará en bucle (cada pocos minutos) para
ir acumulando eventos con timestamp. De momento, una pasada para ver que capta
noticias reales y las analiza.
"""
from __future__ import annotations

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.news import collector, store  # noqa: E402


def main() -> int:
    print("=" * 70)
    print("  RECOLECTOR DE NOTICIAS CRIPTO")
    print("=" * 70)
    print("\nLeyendo feeds RSS...")

    r = collector.recolectar()

    print("\nPor fuente (noticias en el feed):")
    for fuente, n in r["por_fuente"].items():
        estado = f"{n}" if n >= 0 else "FALLO al leer"
        print(f"   {fuente:<16} {estado}")

    print(f"\n  Noticias leidas .............. {r['leidos']}")
    print(f"  Nuevas (no estaban en BD) .... {r['nuevos']}")
    print(f"  Con cripto detectada ......... {r['con_cripto_detectada']}")
    print(f"  Total acumulado en BD ........ {store.total()}")

    if r["muestra"]:
        print("\n  Muestra (mayor carga de sentimiento):")
        print("  " + "-" * 66)
        for e in r["muestra"]:
            signo = "+" if e.sentimiento >= 0 else ""
            activos = ",".join(e.activos)
            print(f"   [{signo}{e.sentimiento:.2f}] {activos:<10} {e.titulo[:48]}")

    print("\n  Los eventos se acumulan en data/news.csv. Cada uno lleva su")
    print("  timestamp para medir despues el drift del precio tras la noticia.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
