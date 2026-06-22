# trading-bot

Bot experimental de trading a corto plazo en cripto. **Empieza en paper trading
(dinero ficticio)** sobre la testnet de Binance y está diseñado para migrar a un
exchange regulado por MiCA (Kraken/Coinbase) cuando —y solo si— las métricas lo
justifiquen.

> ⚠️ **Esto es un experimento.** El trading a corto plazo es estadísticamente
> perdedor para la mayoría de bots retail. El objetivo es aprender, medir con
> honestidad y arriesgar dinero real solo tras superar un gate de validación.

## Decisiones de diseño

- **Mercado: cripto.** 24/7, sin regla PDT, capital fraccionable.
- **Estilo: trend-following / momentum sistemático** en marcos de minutos. No
  scalping de latencia (no competimos con HFT). La ventaja del retail es la
  disciplina sistemática y la gestión de riesgo, no la velocidad.
- **Librería: `ccxt`.** Hablamos con el exchange de forma genérica para poder
  migrar a un exchange MiCA cambiando solo el `.env`.
- **Paper primero: Binance Spot Testnet.** Gratis, dinero ficticio, se resetea
  ~1 vez al mes.

## Plan por fases

1. ✅ **Esqueleto + conexión** (healthcheck contra testnet).
2. ⬜ **Backtester honesto** (con comisiones y slippage).
3. ⬜ **Estrategia trend-following + gestión de riesgo** (stop, sizing por % riesgo).
4. ⬜ **Paper trading en vivo** sobre testnet, con logs de toda la operativa.
5. ⬜ **🚦 Gate de validación**: semanas de métricas en paper *con costes*.
6. ⬜ **Real** en exchange MiCA, capital mínimo. (Requiere confirmación explícita.)

## Puesta en marcha

```bash
# 1. (Opcional pero recomendado) entorno virtual
python -m venv .venv
.venv\Scripts\activate        # Windows PowerShell

# 2. Dependencias
python -m pip install -r requirements.txt

# 3. Configuración
copy .env.example .env        # luego edita .env con tus claves de testnet

# 4. Comprobar que todo conecta
python scripts/healthcheck.py
```

El precio y las velas funcionan **sin claves**. Para ver saldo y operar en paper,
genera claves gratis en https://testnet.binance.vision/ (login con GitHub) y
pégalas en `.env`.
