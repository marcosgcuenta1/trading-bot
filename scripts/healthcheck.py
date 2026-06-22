"""Comprobación de salud: ¿está todo bien conectado?

Ejecuta:   python scripts/healthcheck.py

Verifica, en orden:
  1. Que ccxt puede hablar con el exchange (precio en vivo, sin claves).
  2. Que las velas históricas llegan (las usará el backtester).
  3. Que las claves API funcionan y leen el saldo de la testnet.

Es el primer hito tangible: si esto pasa en verde, la fase 1 está cerrada.
"""
from __future__ import annotations

import sys
from pathlib import Path

# La consola de Windows usa cp1252 y revienta con caracteres no-ASCII
# (nombres de algunos tokens, símbolos...). Forzamos UTF-8 en la salida.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Permite ejecutar el script desde la raíz del proyecto sin instalar nada.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config  # noqa: E402
from src import exchange as ex  # noqa: E402


def main() -> int:
    print("=" * 60)
    print(f"  HEALTH CHECK  |  {config.EXCHANGE.upper()}"
          f"  |  {'TESTNET (dinero ficticio)' if config.TESTNET else 'REAL [!]'}")
    print("=" * 60)

    try:
        bolsa = ex.crear_exchange()
    except Exception as e:  # noqa: BLE001
        print(f"\n[X] No se pudo crear el exchange: {e}")
        return 1

    # 1) Precio en vivo (público) -------------------------------------------
    try:
        precio = ex.precio_actual(bolsa, config.SYMBOL)
        print(f"\n[OK] Conexion OK. {config.SYMBOL} cotiza a {precio:,.2f}")
    except Exception as e:  # noqa: BLE001
        print(f"\n[X] No se pudo obtener el precio: {e}")
        return 1

    # 2) Velas históricas (público) -----------------------------------------
    try:
        v = ex.velas(bolsa, config.SYMBOL, config.TIMEFRAME, limite=5)
        print(f"[OK] Velas {config.TIMEFRAME} OK. Ultima vela (cierre): {v[-1][4]:,.2f}")
    except Exception as e:  # noqa: BLE001
        print(f"[X] No se pudieron obtener velas: {e}")
        return 1

    # 3) Saldo (privado, requiere claves) -----------------------------------
    if not config.tiene_credenciales():
        print("\n[!] Sin claves API en .env todavia.")
        print("    El precio y las velas ya funcionan (es suficiente para")
        print("    backtesting). Para ver saldo y operar en paper, anade las")
        print("    claves de la testnet siguiendo las instrucciones de .env.example")
        return 0

    # Solo nos interesan estos para operar; el resto de la testnet es ruido.
    RELEVANTES = ["USDT", "USDC", "BUSD", "FDUSD", "BTC", "ETH", "BNB"]
    try:
        bal = ex.saldo(bolsa)
        libres = {k: v for k, v in bal.get("free", {}).items() if v and v > 0}
        print("\n[OK] Claves validas. Saldo libre en testnet:")
        if libres:
            for activo in RELEVANTES:
                if activo in libres:
                    print(f"      {activo:>6}: {libres[activo]:,.4f}")
            print(f"      (... y {len(libres)} activos distintos con saldo en total)")
        else:
            print("      (vacio - la testnet pudo resetearse; vuelve a generar fondos)")
    except Exception as e:  # noqa: BLE001
        print(f"\n[X] Las claves no funcionan: {e}")
        return 1

    print("\n" + "=" * 60)
    print("  Fase 1 cerrada. Listo para montar backtester y estrategia.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
