"""¿Las noticias predicen el movimiento del precio? Veredicto sobre lo acumulado.

Ejecuta:   python scripts/measure_drift.py

Cuantos más dias llevemos recolectando noticias, mas fiable es este analisis.
Con pocos eventos, los numeros son anecdota, no evidencia.
"""
from __future__ import annotations

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.news import drift  # noqa: E402


def _media(xs):
    return sum(xs) / len(xs) if xs else 0.0


def main() -> int:
    print("=" * 70)
    print("  MEDIDOR DE DRIFT  |  noticia -> movimiento posterior del precio")
    print("=" * 70)
    print("\nDescargando precios y cruzando con las noticias guardadas...")

    out = drift.medir()
    print(f"\n  Eventos con activo .......... {out['eventos']}")
    print(f"  Mediciones realizadas ....... {out['medibles']}")

    if out["medibles"] == 0:
        print("\n  [!] Aun no hay nada medible: las noticias son demasiado recientes")
        print("      (hace falta que pasen 1-24h tras cada una). Deja el recolector")
        print("      acumulando y vuelve a ejecutar esto dentro de unas horas/dias.")
        return 0

    print("\n  Retorno MEDIO del precio tras la noticia, por sentimiento:")
    print("  " + "-" * 66)
    print(f"  {'Horizonte':<12}{'Positivas':>16}{'Negativas':>16}{'Neutras':>16}")
    print("  " + "-" * 66)
    for h, grupos in out["res"].items():
        pos, neg, neu = grupos["pos"], grupos["neg"], grupos["neu"]
        print(
            f"  {str(h)+'h':<12}"
            f"{_media(pos)*100:>14.3f} %{'':1}"
            f"{_media(neg)*100:>14.3f} %{'':1}"
            f"{_media(neu)*100:>14.3f} %"
        )
        print(f"  {'  (n)':<12}{len(pos):>15}{len(neg):>16}{len(neu):>16}")

    print("\n  COMO LEERLO:")
    print("  Hay senal SOLO si 'Positivas' queda CONSISTENTEMENTE por encima de")
    print("  'Negativas' y con suficientes muestras (n alto). Si estan mezcladas")
    print("  o n es pequeno, NO hay edge demostrado. Paciencia: esto es forward-test.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
