# -*- coding: utf-8 -*-
"""
Módulo de backtesting para estrategias de trading
"""

from .engine import BacktestEngine
from .metrics import (
    calculate_statistics,
    calculate_max_drawdown,
    calculate_profit_factor,
    calculate_sharpe_ratio,
    calculate_sortino_ratio
)
from .visualization import (
    create_performance_chart,
    create_drawdown_chart,
    create_trade_distribution_chart,
    create_monthly_returns_chart,
    create_summary_table
)

__all__ = [
    'BacktestEngine',
    'calculate_statistics',
    'calculate_max_drawdown',
    'calculate_profit_factor',
    'calculate_sharpe_ratio',
    'calculate_sortino_ratio',
    'create_performance_chart',
    'create_drawdown_chart',
    'create_trade_distribution_chart',
    'create_monthly_returns_chart',
    'create_summary_table'
] 