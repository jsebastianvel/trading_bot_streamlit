# Databricks notebook source
# MAGIC %md
# MAGIC # Crypto News + Trading Signals Pipeline
# MAGIC
# MAGIC Ingesta diaria de noticias cripto (RSS publico) + senales tecnicas MACD
# MAGIC multi-timeframe para BTC/USDT, escritas como tablas Delta en Unity Catalog.
# MAGIC
# MAGIC Este notebook corre dentro de un Databricks Repo conectado al repo
# MAGIC publico de GitHub `jsebastianvel/trading_bot_streamlit`, e importa
# MAGIC directamente el codigo real del repo (`utils.api_data.get_price_data`,
# MAGIC `config.TIMEFRAMES`/`SYMBOL`, `genai.news_fetcher.fetch_latest_news`)
# MAGIC en vez de duplicar esa logica.
# MAGIC
# MAGIC **Nota sobre la senal MACD:** la app local (`strategy/macd_strategy.py`)
# MAGIC usa `pandas_ta`, pero ese paquete (el fork mantenido pandas-ta.dev, unica
# MAGIC version publicada en PyPI hoy) requiere Python >=3.12, mientras que el
# MAGIC runtime de Databricks usa Python 3.11 -- no hay ninguna version de
# MAGIC `pandas_ta` instalable aqui. Por eso esta version usa la libreria `ta`
# MAGIC (sin esa restriccion) para calcular MACD/EMA/ATR, replicando exactamente
# MAGIC los mismos umbrales y logica de decision que `check_macd_signal` (incluido
# MAGIC el minimo de 50 periodos para que la EMA-50 sea valida).

# COMMAND ----------

import subprocess, sys

result = subprocess.run(
    [sys.executable, "-m", "pip", "install", "feedparser", "ccxt", "ta", "google-genai"],
    capture_output=True, text=True
)
print(result.stdout[-4000:])
print(result.stderr[-4000:])
if result.returncode != 0:
    dbutils.notebook.exit(f"PIP INSTALL FAILED (rc={result.returncode}): {result.stderr[-2000:]}")

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

import sys
import os
from datetime import datetime, timezone
import pandas as pd
from google import genai
from ta.trend import MACD, EMAIndicator
from ta.volatility import AverageTrueRange

REPO_ROOT = "/Workspace/Repos/jsebastian.velasco@gmail.com/trading_bot_streamlit"
sys.path.append(REPO_ROOT)

from config import TIMEFRAMES, SYMBOL
from utils.api_data import get_price_data
from genai.news_fetcher import fetch_latest_news

CATALOG = "workspace"
SCHEMA = "trading_bot"
NEWS_TABLE = f"{CATALOG}.{SCHEMA}.crypto_news"
SIGNALS_TABLE = f"{CATALOG}.{SCHEMA}.trading_signals"

GEMINI_API_KEY = dbutils.secrets.get(scope="trading_bot_btc", key="gemini_api_key")

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Ingesta de noticias (reutiliza `genai.news_fetcher`)

# COMMAND ----------

articles = fetch_latest_news(max_per_feed=10)
print(f"Articulos obtenidos: {len(articles)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Embeddings (Gemini) y escritura en tabla Delta

# COMMAND ----------

gemini_client = genai.Client(api_key=GEMINI_API_KEY)


def embed_text(text):
    resp = gemini_client.models.embed_content(model="models/gemini-embedding-001", contents=text)
    return resp.embeddings[0].values


ingested_at = datetime.now(timezone.utc)
news_rows = []
for a in articles:
    text = f"{a['title']}. {a['summary']}"
    embedding = embed_text(text)
    news_rows.append({
        "title": a["title"],
        "summary": a["summary"],
        "link": a["link"],
        "source": a["source"],
        "published": a["published"],
        "embedding": embedding,
        "ingested_at": ingested_at,
    })

news_pdf = pd.DataFrame(news_rows)
news_df = spark.createDataFrame(news_pdf)
news_df.write.mode("append").option("mergeSchema", "true").saveAsTable(NEWS_TABLE)
print(f"Escritas {news_df.count()} noticias en {NEWS_TABLE}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Senales MACD multi-timeframe
# MAGIC
# MAGIC Reutiliza `get_price_data`/`TIMEFRAMES`/`SYMBOL` del repo real. El calculo
# MAGIC del indicador usa la libreria `ta` (ver nota arriba) pero replica
# MAGIC exactamente la misma logica de `strategy/macd_strategy.py`.

# COMMAND ----------

def calculate_threshold(timeframe):
    tf_factors = {'15m': 0.5, '30m': 0.6, '1h': 0.7, '4h': 0.8, '1d': 0.9, '3d': 1.0}
    return 0.8 * tf_factors.get(timeframe, 0.7)


def check_macd_signal_databricks(df, timeframe=''):
    """Misma logica que strategy.macd_strategy.check_macd_signal, calculada
    con la libreria `ta` en vez de `pandas_ta` (ver nota de compatibilidad
    de Python arriba)."""
    if len(df) < 50:
        return 'hold', 0.0
    try:
        macd_ind = MACD(close=df['close'], window_fast=12, window_slow=26, window_sign=9)
        last_macd = macd_ind.macd().iloc[-1]
        last_signal = macd_ind.macd_signal().iloc[-1]
        hist = macd_ind.macd_diff()
        last_hist = hist.iloc[-1]
        prev_hist = hist.iloc[-2] if len(df) > 1 else 0
        current_price = df['close'].iloc[-1]

        price_threshold = current_price * 0.001

        atr_ind = AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=14)
        atr_value = atr_ind.average_true_range().iloc[-1]
        volatility = atr_value / price_threshold

        threshold = price_threshold * calculate_threshold(timeframe) * (1 + volatility)

        ema_20 = EMAIndicator(close=df['close'], window=20).ema_indicator().iloc[-1]
        ema_50 = EMAIndicator(close=df['close'], window=50).ema_indicator().iloc[-1]
        trend = 'up' if ema_20 > ema_50 else 'down'

        signal_strength = min((abs(last_hist) / threshold) * (1 + volatility), 1.0)

        if last_hist > 0 and prev_hist <= 0:
            if abs(last_hist) > threshold and trend == 'up':
                return 'valley_buy', signal_strength
            elif trend == 'up':
                return 'buy', signal_strength
        elif last_hist < 0 and prev_hist >= 0:
            if abs(last_hist) > threshold and trend == 'down':
                return 'top_sell', signal_strength
            elif trend == 'down':
                return 'sell', signal_strength
        return 'hold', 0.0
    except Exception as e:
        print(f"Error calculando señal para {timeframe}: {e}")
        return 'hold', 0.0


# COMMAND ----------

# Diagnostico: probar el acceso directo a Binance vs otros exchanges
import ccxt
for exch_name in ['binance', 'kraken', 'coinbase']:
    try:
        exch = getattr(ccxt, exch_name)()
        ohlcv = exch.fetch_ohlcv('BTC/USDT', timeframe='4h', limit=5)
        print(f'{exch_name}: OK, {len(ohlcv)} velas')
    except Exception as e:
        print(f'{exch_name}: FALLO -> {type(e).__name__}: {e}')

# COMMAND ----------

computed_at = datetime.now(timezone.utc)
signal_rows = []
for tf in TIMEFRAMES:
    df = get_price_data(SYMBOL, tf, limit=200)
    if df is None or df.empty:
        print(f"{tf}: sin datos, se omite")
        continue
    signal, strength = check_macd_signal_databricks(df, tf)
    signal_rows.append({
        "symbol": SYMBOL,
        "timeframe": tf,
        "signal": signal,
        "strength": float(strength),
        "price": float(df['close'].iloc[-1]),
        "computed_at": computed_at,
    })
    print(f"{tf}: {signal} (fuerza {strength:.2f})")

if signal_rows:
    signals_pdf = pd.DataFrame(signal_rows)
    signals_df = spark.createDataFrame(signals_pdf)
    signals_df.write.mode("append").option("mergeSchema", "true").saveAsTable(SIGNALS_TABLE)
    print(f"Escritas {signals_df.count()} señales en {SIGNALS_TABLE}")
else:
    print("No se obtuvieron señales (sin datos de precio para ninguna temporalidad), no se escribe nada")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Verificacion rapida

# COMMAND ----------

display(spark.sql(f"SELECT source, title, ingested_at FROM {NEWS_TABLE} ORDER BY ingested_at DESC LIMIT 5"))

# COMMAND ----------

display(spark.sql(f"SELECT timeframe, signal, strength, price, computed_at FROM {SIGNALS_TABLE} ORDER BY computed_at DESC LIMIT 10"))
