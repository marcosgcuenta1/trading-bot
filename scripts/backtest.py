"""Backtest de la estrategia trend-following sobre histórico real.

Ejecuta:   python scripts/backtest.py

Descarga velas reales de mercado, aplica la estrategia, la pasa por el motor de
backtest (con comisiones y slippage) y compara contra comprar y aguantar.
"""
from __future__ import annotations

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd  # noqa: E402

import config  # noqa: E402
from src import backtester as bt  # noqa: E402
from src import exchange as ex  # noqa: E402
from src import strategy as st  # noqa: E402

VELAS = 5000  # ~17 días en 5m


def main() -> int:
    tf = config.TIMEFRAME
    symbol = config.SYMBOL

    print("=" * 64)
    print(f"  BACKTEST  |  {symbol}  |  {tf}  |  estrategia trend-following")
    print("=" * 64)

    print(f"\nDescargando {VELAS} velas reales de mercado ({config.EXCHANGE} mainnet)...")
    bolsa = ex.crear_exchange_datos()
    ohlcv = ex.descargar_historico(bolsa, symbol, tf, velas_totales=VELAS)

    df = pd.DataFrame(ohlcv, columns=["ts", "open", "high", "low", "close", "volume"])
    df["fecha"] = pd.to_datetime(df["ts"], unit="ms")
    print(f"Descargadas {len(df)} velas: del {df['fecha'].iloc[0]} al {df['fecha'].iloc[-1]}")

    # Estrategia -> señales
    params = st.ParametrosEstrategia()
    df = st.generar_senales(df, params)

    # Backtest
    tf_min = bolsa.parse_timeframe(tf) / 60
    res = bt.correr(df, timeframe_min=tf_min, costes=bt.Costes())

    # --- Informe ------------------------------------------------------------
    print("\n" + "-" * 64)
    print(f"  Periodo analizado .......... {res.dias:.1f} dias ({res.velas} velas {tf})")
    print(f"  Operaciones ................ {res.num_operaciones}")
    print(f"  Win rate ................... {res.win_rate*100:.1f} %")
    print(f"  Comisiones+slippage pagado . {res.comisiones_pagadas_pct*100:.2f} % del capital")
    print(f"  Max drawdown ............... {res.max_drawdown*100:.2f} %")
    print(f"  Sharpe (anualizado) ........ {res.sharpe:.2f}")
    print("-" * 64)
    print(f"  RETORNO ESTRATEGIA ......... {res.retorno_estrategia*100:+.2f} %")
    print(f"  Retorno comprar y aguantar . {res.retorno_buy_hold*100:+.2f} %")
    print("-" * 64)

    # --- Veredicto honesto --------------------------------------------------
    bate = res.retorno_estrategia > res.retorno_buy_hold
    print("\n  VEREDICTO:")
    if res.num_operaciones < 5:
        print("  [!] Muy pocas operaciones para concluir nada. Periodo corto o")
        print("      mercado sin tendencia clara. No es estadisticamente fiable.")
    elif bate and res.retorno_estrategia > 0:
        print("  [+] La estrategia bate a comprar y aguantar EN ESTE periodo.")
        print("      Ojo: un periodo no demuestra nada. Hay que probar en varios")
        print("      mercados y epocas antes de confiar.")
    else:
        print("  [-] La estrategia NO bate a comprar y aguantar en este periodo.")
        print("      Es lo normal y lo esperable: la mayoria de estrategias simples")
        print("      no superan al mercado tras costes. Aqui empieza el trabajo real.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
