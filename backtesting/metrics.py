# -*- coding: utf-8 -*-
"""
Funciones para calcular métricas de rendimiento en backtesting
"""

import numpy as np

def calculate_statistics(trades, initial_capital, final_capital):
    """
    Calcula estadísticas de rendimiento para los resultados del backtesting
    
    Args:
        trades: Lista de operaciones realizadas
        initial_capital: Capital inicial
        final_capital: Capital final
        
    Returns:
        dict: Diccionario con estadísticas de rendimiento
    """
    if not trades:
        return {
            'initial_capital': initial_capital,
            'final_capital': final_capital,
            'total_return': 0.0,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0.0,
            'max_drawdown': 0.0,
            'profit_factor': 0.0
        }
    
    # Calcular métricas básicas
    total_trades = len(trades)
    winning_trades = len([t for t in trades if t.get('pnl', 0) > 0])
    losing_trades = len([t for t in trades if t.get('pnl', 0) < 0])
    
    total_pnl = sum(t.get('pnl', 0) for t in trades)
    win_rate = winning_trades / total_trades if total_trades > 0 else 0
    
    # Calcular drawdown
    capital_history = [initial_capital]
    for trade in trades:
        capital_history.append(capital_history[-1] + trade.get('pnl', 0))
    
    max_drawdown = calculate_max_drawdown(capital_history)
    
    # Calcular factor de beneficio
    profit_factor = calculate_profit_factor(trades)
    
    return {
        'initial_capital': initial_capital,
        'final_capital': final_capital,
        'total_return': (final_capital - initial_capital) / initial_capital * 100,
        'total_trades': total_trades,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'win_rate': win_rate * 100,
        'max_drawdown': max_drawdown * 100,
        'profit_factor': profit_factor
    }

def calculate_max_drawdown(capital_history):
    """
    Calcula el máximo drawdown de una serie de capital
    
    Args:
        capital_history: Lista de valores de capital a lo largo del tiempo
        
    Returns:
        float: Máximo drawdown como porcentaje (0-1)
    """
    max_drawdown = 0
    peak = capital_history[0]
    
    for value in capital_history:
        if value > peak:
            peak = value
        drawdown = (peak - value) / peak
        max_drawdown = max(max_drawdown, drawdown)
    
    return max_drawdown

def calculate_profit_factor(trades):
    """
    Calcula el factor de beneficio (ratio entre ganancias y pérdidas)
    
    Args:
        trades: Lista de operaciones realizadas
        
    Returns:
        float: Factor de beneficio
    """
    total_profit = sum(t.get('pnl', 0) for t in trades if t.get('pnl', 0) > 0)
    total_loss = abs(sum(t.get('pnl', 0) for t in trades if t.get('pnl', 0) < 0))
    
    if total_loss == 0:
        return float('inf') if total_profit > 0 else 0.0
    
    return total_profit / total_loss

def calculate_sharpe_ratio(trades, risk_free_rate=0.02):
    """
    Calcula el ratio de Sharpe para las operaciones
    
    Args:
        trades: Lista de operaciones realizadas
        risk_free_rate: Tasa libre de riesgo anual (por defecto 2%)
        
    Returns:
        float: Ratio de Sharpe
    """
    if not trades:
        return 0.0
    
    # Extraer retornos diarios
    returns = [t.get('pnl', 0) for t in trades]
    
    # Calcular retorno medio y desviación estándar
    mean_return = np.mean(returns)
    std_return = np.std(returns)
    
    if std_return == 0:
        return 0.0
    
    # Convertir tasa libre de riesgo a diaria
    daily_rf = (1 + risk_free_rate) ** (1/365) - 1
    
    # Calcular ratio de Sharpe
    sharpe = (mean_return - daily_rf) / std_return
    
    # Anualizar
    return sharpe * np.sqrt(365)

def calculate_sortino_ratio(trades, risk_free_rate=0.02):
    """
    Calcula el ratio de Sortino para las operaciones
    
    Args:
        trades: Lista de operaciones realizadas
        risk_free_rate: Tasa libre de riesgo anual (por defecto 2%)
        
    Returns:
        float: Ratio de Sortino
    """
    if not trades:
        return 0.0
    
    # Extraer retornos diarios
    returns = [t.get('pnl', 0) for t in trades]
    
    # Calcular retorno medio
    mean_return = np.mean(returns)
    
    # Calcular desviación estándar de retornos negativos
    negative_returns = [r for r in returns if r < 0]
    if not negative_returns:
        return float('inf')
    
    downside_std = np.std(negative_returns)
    
    if downside_std == 0:
        return 0.0
    
    # Convertir tasa libre de riesgo a diaria
    daily_rf = (1 + risk_free_rate) ** (1/365) - 1
    
    # Calcular ratio de Sortino
    sortino = (mean_return - daily_rf) / downside_std
    
    # Anualizar
    return sortino * np.sqrt(365) 