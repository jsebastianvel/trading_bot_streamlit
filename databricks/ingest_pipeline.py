# Databricks notebook source
# MAGIC %md
# MAGIC # Crypto News + Trading Signals Pipeline
# MAGIC
# MAGIC Ingesta diaria de noticias cripto (RSS publico) + senales tecnicas MACD
# MAGIC multi-timeframe para BTC/USDT, escritas como tablas Delta en Unity Catalog.
# MAGIC
# MAGIC Este notebook corre dentro de un Databricks Repo conectado al repo
# MAGIC publico de GitHub `jsebastianvel/trading_bot_streamlit`, e importa
# MAGIC directamente el codigo real del repo (`strategy`, `utils`, `config`,
# MAGIC `genai.news_fetcher`) en vez de duplicar la logica -- es la misma
# MAGIC estrategia MACD+EMA que corre en la app de Streamlit local, incluyendo
# MAGIC el fix del minimo de 50 periodos para EMA-50.

# COMMAND ----------

import subprocess, sys

result = subprocess.run(
    [sys.executable, "-m", "pip", "install", "feedparser", "ccxt", "pandas_ta", "google-genai"],
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

REPO_ROOT = "/Workspace/Repos/jsebastian.velasco@gmail.com/trading_bot_streamlit"
sys.path.append(REPO_ROOT)

from config import TIMEFRAMES, SYMBOL
from utils.api_data import get_price_data
from strategy.macd_strategy import check_macd_signal
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
# MAGIC ## 3. Senales MACD multi-timeframe (reutiliza `strategy.macd_strategy` y `utils.api_data`)

# COMMAND ----------

computed_at = datetime.now(timezone.utc)
signal_rows = []
for tf in TIMEFRAMES:
    df = get_price_data(SYMBOL, tf, limit=200)
    if df is None or df.empty:
        print(f"{tf}: sin datos, se omite")
        continue
    signal, strength = check_macd_signal(df, tf)
    signal_rows.append({
        "symbol": SYMBOL,
        "timeframe": tf,
        "signal": signal,
        "strength": float(strength),
        "price": float(df['close'].iloc[-1]),
        "computed_at": computed_at,
    })
    print(f"{tf}: {signal} (fuerza {strength:.2f})")

signals_pdf = pd.DataFrame(signal_rows)
signals_df = spark.createDataFrame(signals_pdf)
signals_df.write.mode("append").option("mergeSchema", "true").saveAsTable(SIGNALS_TABLE)
print(f"Escritas {signals_df.count()} señales en {SIGNALS_TABLE}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Verificacion rapida

# COMMAND ----------

display(spark.sql(f"SELECT source, title, ingested_at FROM {NEWS_TABLE} ORDER BY ingested_at DESC LIMIT 5"))

# COMMAND ----------

display(spark.sql(f"SELECT timeframe, signal, strength, price, computed_at FROM {SIGNALS_TABLE} ORDER BY computed_at DESC LIMIT 10"))
