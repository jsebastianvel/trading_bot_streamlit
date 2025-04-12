# -*- coding: utf-8 -*-
"""
Funciones para visualizar resultados de backtesting
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

def create_performance_chart(results, start_date, end_date):
    """
    Crea un gráfico de rendimiento para los resultados del backtesting
    
    Args:
        results: Diccionario con resultados del backtesting
        start_date: Fecha de inicio
        end_date: Fecha de fin
        
    Returns:
        plotly.graph_objects.Figure: Gráfico de rendimiento
    """
    # Crear datos para el gráfico
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    capital = results['initial_capital']
    capital_history = [capital]
    
    # Simular crecimiento lineal para visualización
    for i in range(1, len(dates)):
        daily_return = results['total_return'] / len(dates)
        capital *= (1 + daily_return/100)
        capital_history.append(capital)
    
    # Crear DataFrame para el gráfico
    df = pd.DataFrame({
        'Fecha': dates,
        'Capital': capital_history
    })
    
    # Gráfico de línea
    fig = px.line(
        df, 
        x='Fecha', 
        y='Capital',
        title='Evolución del Capital',
        labels={'Capital': 'Capital ($)', 'Fecha': 'Fecha'}
    )
    
    return fig

def create_drawdown_chart(results, start_date, end_date):
    """
    Crea un gráfico de drawdown para los resultados del backtesting
    
    Args:
        results: Diccionario con resultados del backtesting
        start_date: Fecha de inicio
        end_date: Fecha de fin
        
    Returns:
        plotly.graph_objects.Figure: Gráfico de drawdown
    """
    # Crear datos para el gráfico
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    capital = results['initial_capital']
    capital_history = [capital]
    
    # Simular crecimiento lineal para visualización
    for i in range(1, len(dates)):
        daily_return = results['total_return'] / len(dates)
        capital *= (1 + daily_return/100)
        capital_history.append(capital)
    
    # Simular drawdown para visualización
    peak = results['initial_capital']
    drawdown_history = []
    
    for capital in capital_history:
        if capital > peak:
            peak = capital
        drawdown = (peak - capital) / peak * 100
        drawdown_history.append(drawdown)
    
    # Crear DataFrame para el gráfico de drawdown
    df_drawdown = pd.DataFrame({
        'Fecha': dates,
        'Drawdown': drawdown_history
    })
    
    # Gráfico de área para drawdown
    fig = px.area(
        df_drawdown, 
        x='Fecha', 
        y='Drawdown',
        title='Drawdown Histórico',
        labels={'Drawdown': 'Drawdown (%)', 'Fecha': 'Fecha'}
    )
    
    return fig

def create_trade_distribution_chart(trades):
    """
    Crea un gráfico de distribución de operaciones
    
    Args:
        trades: Lista de operaciones realizadas
        
    Returns:
        plotly.graph_objects.Figure: Gráfico de distribución de operaciones
    """
    if not trades:
        # Crear un gráfico vacío si no hay operaciones
        fig = go.Figure()
        fig.add_annotation(
            text="No hay operaciones para mostrar",
            xref="paper", yref="paper",
            showarrow=False, font=dict(size=14)
        )
        return fig
    
    # Extraer P&L de cada operación
    pnl_values = [t.get('pnl', 0) for t in trades]
    
    # Crear histograma
    fig = px.histogram(
        pnl_values,
        title='Distribución de P&L por Operación',
        labels={'value': 'P&L ($)', 'count': 'Número de Operaciones'},
        nbins=20
    )
    
    # Añadir línea vertical en 0
    fig.add_vline(x=0, line_dash="dash", line_color="red")
    
    return fig

def create_monthly_returns_chart(trades, start_date, end_date):
    """
    Crea un gráfico de retornos mensuales
    
    Args:
        trades: Lista de operaciones realizadas
        start_date: Fecha de inicio
        end_date: Fecha de fin
        
    Returns:
        plotly.graph_objects.Figure: Gráfico de retornos mensuales
    """
    if not trades:
        # Crear un gráfico vacío si no hay operaciones
        fig = go.Figure()
        fig.add_annotation(
            text="No hay operaciones para mostrar",
            xref="paper", yref="paper",
            showarrow=False, font=dict(size=14)
        )
        return fig
    
    # Crear DataFrame con operaciones
    df_trades = pd.DataFrame(trades)
    
    # Asegurarse de que las fechas están en formato datetime
    df_trades['exit_time'] = pd.to_datetime(df_trades['exit_time'])
    
    # Agrupar por mes y sumar P&L
    df_trades['month'] = df_trades['exit_time'].dt.to_period('M')
    monthly_returns = df_trades.groupby('month')['pnl'].sum().reset_index()
    monthly_returns['month'] = monthly_returns['month'].astype(str)
    
    # Crear gráfico de barras
    fig = px.bar(
        monthly_returns,
        x='month',
        y='pnl',
        title='Retornos Mensuales',
        labels={'month': 'Mes', 'pnl': 'P&L ($)'},
        color='pnl',
        color_continuous_scale=['red', 'green']
    )
    
    return fig

def create_summary_table(results):
    """
    Crea una tabla de resumen con los resultados del backtesting
    
    Args:
        results: Diccionario con resultados del backtesting
        
    Returns:
        plotly.graph_objects.Figure: Tabla de resumen
    """
    # Crear DataFrame con resultados
    df = pd.DataFrame({
        'Métrica': [
            'Capital Inicial',
            'Capital Final',
            'Retorno Total',
            'Operaciones Totales',
            'Operaciones Ganadoras',
            'Operaciones Perdedoras',
            'Win Rate',
            'Máximo Drawdown',
            'Factor de Beneficio'
        ],
        'Valor': [
            f"${results['initial_capital']:,.2f}",
            f"${results['final_capital']:,.2f}",
            f"{results['total_return']:.2f}%",
            results['total_trades'],
            results['winning_trades'],
            results['losing_trades'],
            f"{results['win_rate']:.2f}%",
            f"{results['max_drawdown']:.2f}%",
            f"{results['profit_factor']:.2f}"
        ]
    })
    
    # Crear tabla
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['Métrica', 'Valor'],
            fill_color='paleturquoise',
            align='left'
        ),
        cells=dict(
            values=[df['Métrica'], df['Valor']],
            fill_color='lavender',
            align='left'
        )
    )])
    
    fig.update_layout(
        title='Resumen de Resultados',
        width=600,
        height=400
    )
    
    return fig 