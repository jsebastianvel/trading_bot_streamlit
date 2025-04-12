# Análisis Técnico y Proceso de Decisión

## Indicadores Técnicos

### MACD (Moving Average Convergence Divergence)
El MACD es el indicador principal utilizado en la estrategia. Se calcula de la siguiente manera:

1. **Cálculo del MACD**:
   - EMA rápida (12 períodos)
   - EMA lenta (26 períodos)
   - Línea de señal (EMA de 9 períodos del MACD)
   - Histograma (diferencia entre MACD y línea de señal)

2. **Señales MACD**:
   - **Valley Buy**: Cuando el histograma está por debajo de -0.5 y la línea MACD cruza por encima de la línea de señal
   - **Top Sell**: Cuando el histograma está por encima de 0.5 y la línea MACD cruza por debajo de la línea de señal
   - **Buy**: Cuando la línea MACD está por encima de la línea de señal
   - **Sell**: Cuando la línea MACD está por debajo de la línea de señal

### ATR (Average True Range)
Se utiliza para medir la volatilidad y ajustar los umbrales de las señales:
- Período: 14
- Se calcula como: `max(high - low, |high - close_prev|, |low - close_prev|)`
- Se utiliza para ajustar dinámicamente los umbrales de las señales según la volatilidad del mercado

## Proceso de Decisión

### 1. Análisis Multi-Timeframe
La estrategia analiza 6 timeframes diferentes con los siguientes pesos:

| Timeframe | Peso | Descripción |
|-----------|------|-------------|
| 15m       | 0.1  | Señales de muy corto plazo |
| 30m       | 0.2  | Señales de corto plazo |
| 1h        | 0.4  | Señales de medio plazo |
| 4h        | 1.0  | Señales de largo plazo |
| 1d        | 5.0  | Señales de muy largo plazo |
| 3d        | 15.0 | Señales de tendencia principal |

### 2. Cálculo de Fuerza de Señal
Para cada timeframe:
1. Se calcula un umbral base según la temporalidad
2. Se ajusta el umbral según la volatilidad (ATR)
3. Se calcula la fuerza de la señal (0 a 1) basada en:
   - Magnitud del histograma MACD
   - Umbral dinámico ajustado
   - Peso del timeframe

### 3. Ponderación de Señales
Las señales se ponderan según:
- Tipo de señal (valley_buy/top_sell = 1.5x, buy/sell = 1.0x)
- Fuerza de la señal (0-1)
- Peso del timeframe

### 4. Decisión Final
La decisión final se toma considerando:

1. **Peso Total de Compra vs Venta**:
   - Se suman todos los pesos de señales de compra
   - Se suman todos los pesos de señales de venta
   - Se compara la diferencia con el umbral configurado (SIGNAL_THRESHOLD = 2.0)

2. **Resultados Posibles**:
   - **LONG**: Si (peso_buy - peso_sell) ≥ SIGNAL_THRESHOLD
   - **SHORT**: Si (peso_sell - peso_buy) ≥ SIGNAL_THRESHOLD
   - **WAIT**: Si la diferencia es menor al umbral

### 5. Confirmación con Order Book
La decisión se complementa con el análisis del order book:
- Top 10 posiciones de compra y venta
- Volumen en BTC y USD
- Concentración de órdenes
- Spread y precio medio

## Notas Importantes

1. **Timeframe Principal**: 
   - La decisión final se toma principalmente en el timeframe de 4 horas (1d)
   - Los timeframes más largos (1d, 3d) tienen mayor peso para confirmar la tendencia
   - Los timeframes más cortos (15m, 30m) se usan para timing de entrada

2. **Ajustes Dinámicos**:
   - Los umbrales se ajustan según la volatilidad del mercado
   - Las señales más fuertes (valley_buy/top_sell) tienen mayor peso
   - El sistema es más conservador en timeframes largos

3. **Gestión de Riesgo**:
   - Se considera la volatilidad (ATR) para ajustar posiciones
   - Se monitorea la concentración de órdenes en el order book
   - Se evitan señales contradictorias entre timeframes 