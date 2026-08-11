# -*- coding: utf-8 -*-
"""Agent that combines the existing MACD multi-timeframe strategy with
RAG-retrieved crypto news, and asks an LLM to produce an explained,
natural-language trading recommendation."""

from config import TIMEFRAMES, SYMBOL, SIGNAL_THRESHOLD
from utils.api_data import get_price_data
from strategy.macd_strategy import check_macd_signal
from genai.rag_store import query_relevant_news, build_index
from genai.news_fetcher import fetch_latest_news
from genai.llm_client import generate_text

SIGNAL_WEIGHTS = {'buy': 1.0, 'sell': 1.0, 'valley_buy': 1.5, 'top_sell': 1.5, 'hold': 0.0}


def _aggregate_signals(symbol):
    peso_buy = 0.0
    peso_sell = 0.0
    resumen = []
    for tf, peso_tf in TIMEFRAMES.items():
        df = get_price_data(symbol, tf, limit=200)
        if df is None or df.empty:
            resumen.append(f"{tf}: sin datos")
            continue
        signal, strength = check_macd_signal(df, timeframe=tf)
        peso_signal = SIGNAL_WEIGHTS.get(signal, 0) * strength
        if signal in ('buy', 'valley_buy'):
            peso_buy += peso_tf * peso_signal
        elif signal in ('sell', 'top_sell'):
            peso_sell += peso_tf * peso_signal
        resumen.append(f"{tf}: {signal} (fuerza {strength:.2f})")
    return peso_buy, peso_sell, resumen


def generate_market_brief(symbol=SYMBOL, lang="es"):
    """Combines technical MACD signals with RAG-retrieved news to produce
    an LLM-generated, explained trading recommendation."""
    try:
        articles = fetch_latest_news(max_per_feed=5)
        build_index(articles)
    except Exception as e:
        print(f"No se pudo refrescar el indice de noticias: {e}")

    peso_buy, peso_sell, resumen = _aggregate_signals(symbol)

    if peso_buy - peso_sell >= SIGNAL_THRESHOLD:
        decision = "LONG"
    elif peso_sell - peso_buy >= SIGNAL_THRESHOLD:
        decision = "SHORT"
    else:
        decision = "WAIT"

    news = query_relevant_news(f"{symbol} price news market", top_k=5)
    news_lines = "\n".join(f"- ({n['source']}) {n['title']}" for n in news) or "No hay noticias indexadas todavia."
    signals_lines = "\n".join(resumen)

    if lang == "en":
        instructions = (
            "Write a short market brief (max 150 words) in English that:\n"
            "1. Explains in plain language what the technical analysis shows.\n"
            "2. States whether recent news reinforces or contradicts the technical signal.\n"
            "3. Gives a clear final recommendation (LONG, SHORT, or WAIT) with reasoning.\n"
            "Do not invent prices or data that are not in the context above."
        )
    else:
        instructions = (
            "Escribe un market brief breve (maximo 150 palabras) en espanol que:\n"
            "1. Explique en lenguaje sencillo que dice el analisis tecnico.\n"
            "2. Indique si las noticias recientes refuerzan o contradicen la senal tecnica.\n"
            "3. De una recomendacion final clara (LONG, SHORT o WAIT) con el razonamiento.\n"
            "No inventes precios ni datos que no esten en el contexto de arriba."
        )

    prompt = f"""Eres un analista financiero cuantitativo. Tienes dos fuentes de informacion sobre {symbol}:

SENALES TECNICAS (indicador MACD por temporalidad):
{signals_lines}

Decision preliminar del sistema (basada solo en pesos tecnicos): {decision}
(peso compra: {peso_buy:.2f}, peso venta: {peso_sell:.2f})

NOTICIAS RECIENTES RELEVANTES:
{news_lines}

{instructions}"""

    explanation = generate_text(prompt)

    return {
        "symbol": symbol,
        "decision": decision,
        "peso_buy": peso_buy,
        "peso_sell": peso_sell,
        "signals": resumen,
        "news": news,
        "explanation": explanation,
    }


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    brief = generate_market_brief()
    print(f"Decision tecnica: {brief['decision']}")
    print("\n--- Market Brief (LLM) ---")
    print(brief["explanation"])
