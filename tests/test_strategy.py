# -*- coding: utf-8 -*-
"""
Tests para la estrategia MACD
"""

import unittest
import pandas as pd
import numpy as np
from strategy.macd_strategy import check_macd_signal, calculate_threshold

class TestMACDStrategy(unittest.TestCase):
    def setUp(self):
        """Preparar datos para las pruebas"""
        # Crear datos sintéticos para pruebas
        dates = pd.date_range(start='2024-01-01', periods=100, freq='1H')
        self.test_data = pd.DataFrame({
            'open': np.random.random(100) * 100 + 30000,
            'high': np.random.random(100) * 100 + 30100,
            'low': np.random.random(100) * 100 + 29900,
            'close': np.random.random(100) * 100 + 30000,
            'volume': np.random.random(100) * 1000
        }, index=dates)

    def test_calculate_threshold(self):
        """Probar el cálculo de umbrales"""
        # Probar diferentes timeframes
        timeframes = ['15m', '30m', '1h', '4h', '1d', '3d']
        for tf in timeframes:
            threshold = calculate_threshold(tf)
            self.assertGreater(threshold, 0)
            self.assertLess(threshold, 1)

    def test_check_macd_signal(self):
        """Probar la generación de señales MACD"""
        # Probar con diferentes timeframes
        timeframes = ['1h', '4h']
        for tf in timeframes:
            signal, strength = check_macd_signal(self.test_data, tf)
            
            # Verificar el tipo de señal
            self.assertIn(signal, ['buy', 'sell', 'valley_buy', 'top_sell', 'hold'])
            
            # Verificar la fuerza de la señal
            self.assertGreaterEqual(strength, 0)
            self.assertLessEqual(strength, 1)

    def test_signal_consistency(self):
        """Probar la consistencia de las señales"""
        # Generar la misma señal dos veces con los mismos datos
        signal1, strength1 = check_macd_signal(self.test_data, '1h')
        signal2, strength2 = check_macd_signal(self.test_data, '1h')
        
        # Las señales deben ser idénticas
        self.assertEqual(signal1, signal2)
        self.assertEqual(strength1, strength2)

if __name__ == '__main__':
    unittest.main() 