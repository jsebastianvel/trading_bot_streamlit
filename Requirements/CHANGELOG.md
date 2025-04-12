# Registro de Cambios (Changelog)

## [2025-04-11]

### Interfaz de Backtesting con Streamlit
- **[01:30]** Implementación de interfaz visual para backtesting
  - Creado script `run_backtest.py` para ejecutar backtesting con parámetros configurables
  - Desarrollada aplicación Streamlit (`app_streamlit.py`) para visualización de resultados
  - Añadidos gráficos interactivos de rendimiento y drawdown
  - Implementado almacenamiento de resultados en formato JSON
  - Añadida selección de parámetros de backtesting (par de trading, días, capital)

### Cambios en Visualización
- **[00:15]** Reemplazo de Plotly por Matplotlib
  - Cambiado sistema de visualización de gráficos MACD
  - Eliminada dependencia de Kaleido
  - Mejorada compatibilidad con diferentes sistemas operativos
  - Añadido soporte para exportación en PDF como alternativa

## [2025-04-10]

### Implementación de Backtesting
- **[23:55]** Nuevo sistema de backtesting (`utils/backtesting.py`)
  - Clase `BacktestEngine` para simulación de estrategias
  - Soporte para múltiples timeframes
  - Simulación de operaciones long/short
  - Cálculo de métricas de rendimiento:
    * Retorno total y por operación
    * Win rate y ratio de beneficio
    * Máximo drawdown
    * Análisis de operaciones ganadoras/perdedoras
  - Visualización detallada de resultados
  - Integración con la estrategia MACD existente

### Mejoras en Sistema MACD
- **[23:45]** Implementación del sistema de notificaciones Telegram
  - Creado nuevo módulo `utils/telegram_notifications.py`
  - Añadida clase `TelegramNotifier` con soporte para diferentes tipos de mensajes
  - Integración con el sistema principal en `main.py`
  - Añadido archivo `TELEGRAM_SETUP.txt` con instrucciones de configuración

- **[23:32]** Mejoras en visualización MACD (`visual/macd_plot.py`)
  - Implementación de gráficos con plotly
  - Soporte para múltiples timeframes
  - Añadida visualización de señales de compra/venta
  - Mejora en el formato y diseño de gráficos
  - Manejo de errores en generación de imágenes
  - Soporte para guardado en PNG y HTML

- **[22:47]** Actualización de estrategia MACD (`strategy/macd_strategy.py`)
  - Implementación de umbrales dinámicos basados en timeframe
  - Añadido sistema de pesos ponderados
  - Integración de factor de volatilidad usando ATR
  - Mejora en el cálculo de fuerza de señales
  - Optimización de señales valley_buy y top_sell

### Actualizaciones de Configuración
- **[22:56]** Mejoras en configuración (`config.py`)
  - Configuración de timeframes con pesos
  - Ajuste de umbrales de señal
  - Configuración de par de trading (BTC/USDT)

### Dependencias
- Actualización de `library requirements.txt`
  - Añadido plotly para visualizaciones
  - Añadido kaleido para exportación de imágenes
  - Añadido requests para API de Telegram
  - Añadido python-telegram-bot para notificaciones
  - Añadido python-dotenv para variables de entorno

### Estructura del Proyecto
- Organización modular del código
  - Módulo `strategy/` para lógica de trading
  - Módulo `visual/` para generación de gráficos
  - Módulo `utils/` para utilidades generales
  - Directorio `charts/` para almacenamiento de gráficos

## Pendientes
- [ ] Optimizar parámetros de la estrategia usando resultados del backtesting
- [ ] Añadir visualización de resultados del backtesting
- [ ] Implementar análisis de riesgo y Kelly Criterion
- [ ] Añadir más indicadores técnicos para confirmación
- [ ] Mejorar documentación del código
- [ ] Añadir tests unitarios
- [ ] Optimizar uso de memoria en análisis multi-timeframe

## [0.2.0] - 2024-04-11

### Cambiado
- Gestión de riesgo más conservadora:
  - Reducido el tamaño máximo de posición de 95% a 5% del capital
  - Mantenidos los niveles de stop loss (2%) y take profit (4%)

- Mejora en la lógica del MACD:
  - Umbral dinámico basado en el precio actual (0.1% del precio)
  - Ajuste por volatilidad usando ATR
  - Mejor manejo de señales según la temporalidad

- Nueva distribución de pesos por temporalidad usando Fibonacci:
  - 15m: 1 (peso mínimo)
  - 30m: 2
  - 1h: 3
  - 4h: 5
  - 1d: 8
  - 3d: 13

### Arreglado
- Corrección en el manejo de timestamps en la visualización
- Mejor manejo de errores en la carga de datos históricos

## [0.1.0] - 2024-04-10

### Añadido
- Implementación inicial del bot de trading
- Estrategia basada en MACD
- Interfaz de usuario con Streamlit
- Backtesting con múltiples temporalidades
- Visualización de resultados con gráficos interactivos
- Sistema de gestión de riesgo básico

### Características del Backtesting
- **Gestión de Datos**:
  - Descarga automática de datos históricos de Binance
  - Almacenamiento local en formato CSV
  - Soporte para múltiples timeframes (1h, 4h, 1d)
  - Caché de datos para optimizar rendimiento

- **Procesamiento de Señales**:
  - Implementación de estrategia MACD
  - Sistema de pesos para diferentes timeframes
  - Umbrales configurables para señales
  - Combinación de señales de múltiples timeframes

- **Gestión de Posiciones**:
  - Soporte para posiciones long y short
  - Cálculo de tamaño de posición basado en capital
  - Gestión de riesgo por operación
  - Registro detallado de trades

- **Métricas y Análisis**:
  - Cálculo de retorno total
  - Win rate y factor de beneficio
  - Máximo drawdown
  - Ratio de Sharpe y Sortino
  - Estadísticas detalladas por trade

- **Almacenamiento y Reportes**:
  - Guardado de resultados en JSON
  - Directorio dedicado para datos históricos
  - Directorio para resultados de backtesting
  - Nombres de archivo con timestamp y parámetros

### Mejorado
- Optimización del rendimiento del backtesting
- Mejor manejo de errores y excepciones
- Documentación detallada del código
- Mensajes informativos durante la ejecución

### Corregido
- Errores en el cálculo de P&L
- Problemas con la gestión de timeframes
- Inconsistencias en el manejo de fechas
- Errores en la serialización de resultados

### Cambios Técnicos
- Refactorización del motor de backtesting
- Implementación de sistema de caché para datos
- Mejora en el manejo de memoria
- Optimización de operaciones con DataFrames

### Documentación
- Documentación detallada del sistema de backtesting
- Ejemplos de uso y configuración
- Descripción de métricas y parámetros
- Guía de interpretación de resultados 