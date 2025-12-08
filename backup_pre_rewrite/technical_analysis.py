"""
TECHNICAL ANALYSIS MODULE
================================================================================
Comprehensive technical indicators for stock analysis.

Features:
- Moving Averages (SMA, EMA)
- Momentum Indicators (RSI, MACD)
- Volatility Indicators (Bollinger Bands, ATR)
- Support/Resistance Levels
- Chart Pattern Detection

Data Source: Historical price data (pandas DataFrame)
Author: Atlas Financial Intelligence
Date: November 2025
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta


class TechnicalAnalysis:
    """
    Comprehensive technical analysis calculator
    """
    
    def __init__(self, price_data: pd.DataFrame):
        """
        Initialize with historical price data
        
        Args:
            price_data: DataFrame with columns ['Open', 'High', 'Low', 'Close', 'Volume']
                       and datetime index
        """
        self.data = price_data.copy()
        self.close = self.data['Close']
        self.high = self.data['High']
        self.low = self.data['Low']
        self.volume = self.data['Volume']
        
    # ========================================================================
    # MOVING AVERAGES
    # ========================================================================
    
    def calculate_sma(self, period: int = 20) -> pd.Series:
        """Calculate Simple Moving Average"""
        return self.close.rolling(window=period).mean()
    
    def calculate_ema(self, period: int = 20) -> pd.Series:
        """Calculate Exponential Moving Average"""
        return self.close.ewm(span=period, adjust=False).mean()
    
    def calculate_moving_averages(self) -> Dict[str, pd.Series]:
        """Calculate all standard moving averages"""
        return {
            'SMA_20': self.calculate_sma(20),
            'SMA_50': self.calculate_sma(50),
            'SMA_200': self.calculate_sma(200),
            'EMA_12': self.calculate_ema(12),
            'EMA_26': self.calculate_ema(26),
            'EMA_50': self.calculate_ema(50)
        }
    
    # ========================================================================
    # MOMENTUM INDICATORS
    # ========================================================================
    
    def calculate_rsi(self, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI)
        
        Returns:
            Series with RSI values (0-100)
        """
        delta = self.close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_macd(self, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Returns:
            Dictionary with 'macd', 'signal', 'histogram'
        """
        ema_fast = self.calculate_ema(fast)
        ema_slow = self.calculate_ema(slow)
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    def calculate_stochastic(self, k_period: int = 14, d_period: int = 3) -> Dict[str, pd.Series]:
        """
        Calculate Stochastic Oscillator
        
        Returns:
            Dictionary with '%K' and '%D'
        """
        low_min = self.low.rolling(window=k_period).min()
        high_max = self.high.rolling(window=k_period).max()
        
        k_percent = 100 * ((self.close - low_min) / (high_max - low_min))
        d_percent = k_percent.rolling(window=d_period).mean()
        
        return {
            'k_percent': k_percent,
            'd_percent': d_percent
        }
    
    # ========================================================================
    # VOLATILITY INDICATORS
    # ========================================================================
    
    def calculate_bollinger_bands(self, period: int = 20, std_dev: float = 2.0) -> Dict[str, pd.Series]:
        """
        Calculate Bollinger Bands
        
        Returns:
            Dictionary with 'upper', 'middle', 'lower', 'bandwidth'
        """
        middle = self.calculate_sma(period)
        std = self.close.rolling(window=period).std()
        
        upper = middle + (std_dev * std)
        lower = middle - (std_dev * std)
        bandwidth = (upper - lower) / middle
        
        return {
            'upper': upper,
            'middle': middle,
            'lower': lower,
            'bandwidth': bandwidth
        }
    
    def calculate_atr(self, period: int = 14) -> pd.Series:
        """
        Calculate Average True Range (ATR)
        Measures volatility
        """
        high_low = self.high - self.low
        high_close = np.abs(self.high - self.close.shift())
        low_close = np.abs(self.low - self.close.shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()
        
        return atr
    
    # ========================================================================
    # VOLUME INDICATORS
    # ========================================================================
    
    def calculate_obv(self) -> pd.Series:
        """
        Calculate On-Balance Volume (OBV)
        Cumulative volume indicator
        """
        obv = (np.sign(self.close.diff()) * self.volume).fillna(0).cumsum()
        return obv
    
    def calculate_volume_sma(self, period: int = 20) -> pd.Series:
        """Calculate Volume Moving Average"""
        return self.volume.rolling(window=period).mean()
    
    # ========================================================================
    # TREND INDICATORS
    # ========================================================================
    
    def calculate_adx(self, period: int = 14) -> pd.Series:
        """
        Calculate Average Directional Index (ADX)
        Measures trend strength (0-100)
        """
        high_diff = self.high.diff()
        low_diff = -self.low.diff()
        
        plus_dm = np.where((high_diff > low_diff) & (high_diff > 0), high_diff, 0)
        minus_dm = np.where((low_diff > high_diff) & (low_diff > 0), low_diff, 0)
        
        atr = self.calculate_atr(period)
        
        plus_di = 100 * pd.Series(plus_dm, index=self.data.index).rolling(window=period).mean() / atr
        minus_di = 100 * pd.Series(minus_dm, index=self.data.index).rolling(window=period).mean() / atr
        
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        
        return adx
    
    # ========================================================================
    # SUPPORT & RESISTANCE
    # ========================================================================
    
    def find_support_resistance(self, window: int = 20, num_levels: int = 3) -> Dict[str, List[float]]:
        """
        Find key support and resistance levels using local extrema
        
        Returns:
            Dictionary with 'support' and 'resistance' lists
        """
        # Find local maxima (resistance)
        local_max = self.high.rolling(window=window, center=True).max()
        resistance = self.high[self.high == local_max].nlargest(num_levels).values.tolist()
        
        # Find local minima (support)
        local_min = self.low.rolling(window=window, center=True).min()
        support = self.low[self.low == local_min].nsmallest(num_levels).values.tolist()
        
        return {
            'support': sorted(support),
            'resistance': sorted(resistance, reverse=True)
        }
    
    # ========================================================================
    # SIGNALS & ANALYSIS
    # ========================================================================
    
    def get_current_signals(self) -> Dict:
        """
        Get current technical signals and indicators
        
        Returns comprehensive technical analysis snapshot
        """
        current_price = self.close.iloc[-1]
        
        # Moving Averages
        mas = self.calculate_moving_averages()
        sma_20 = mas['SMA_20'].iloc[-1]
        sma_50 = mas['SMA_50'].iloc[-1]
        sma_200 = mas['SMA_200'].iloc[-1]
        
        # RSI
        rsi = self.calculate_rsi().iloc[-1]
        
        # MACD
        macd_data = self.calculate_macd()
        macd_current = macd_data['macd'].iloc[-1]
        signal_current = macd_data['signal'].iloc[-1]
        histogram_current = macd_data['histogram'].iloc[-1]
        
        # Bollinger Bands
        bb = self.calculate_bollinger_bands()
        bb_upper = bb['upper'].iloc[-1]
        bb_lower = bb['lower'].iloc[-1]
        bb_middle = bb['middle'].iloc[-1]
        
        # ATR (Volatility)
        atr = self.calculate_atr().iloc[-1]
        
        # Volume
        volume_sma = self.calculate_volume_sma().iloc[-1]
        current_volume = self.volume.iloc[-1]
        
        # Support/Resistance
        sr_levels = self.find_support_resistance()
        
        # Signal Interpretation
        signals = {
            'price': current_price,
            'moving_averages': {
                'sma_20': sma_20,
                'sma_50': sma_50,
                'sma_200': sma_200,
                'price_vs_sma20': 'Above' if current_price > sma_20 else 'Below',
                'price_vs_sma50': 'Above' if current_price > sma_50 else 'Below',
                'price_vs_sma200': 'Above' if current_price > sma_200 else 'Below',
                'golden_cross': sma_50 > sma_200,  # Bullish
                'death_cross': sma_50 < sma_200    # Bearish
            },
            'momentum': {
                'rsi': rsi,
                'rsi_signal': self._interpret_rsi(rsi),
                'macd': macd_current,
                'macd_signal': signal_current,
                'macd_histogram': histogram_current,
                'macd_crossover': 'Bullish' if histogram_current > 0 else 'Bearish'
            },
            'volatility': {
                'atr': atr,
                'atr_pct': (atr / current_price) * 100,
                'bollinger_upper': bb_upper,
                'bollinger_middle': bb_middle,
                'bollinger_lower': bb_lower,
                'bb_position': self._bb_position(current_price, bb_lower, bb_upper)
            },
            'volume': {
                'current': current_volume,
                'sma_20': volume_sma,
                'relative': 'High' if current_volume > volume_sma * 1.5 else 'Normal' if current_volume > volume_sma * 0.7 else 'Low'
            },
            'levels': sr_levels,
            'overall_signal': self._generate_overall_signal(current_price, sma_50, sma_200, rsi, histogram_current)
        }
        
        return signals
    
    def _interpret_rsi(self, rsi: float) -> str:
        """Interpret RSI value"""
        if rsi >= 70:
            return 'Overbought (Sell Signal)'
        elif rsi >= 60:
            return 'Strong'
        elif rsi >= 40:
            return 'Neutral'
        elif rsi >= 30:
            return 'Weak'
        else:
            return 'Oversold (Buy Signal)'
    
    def _bb_position(self, price: float, lower: float, upper: float) -> str:
        """Determine position within Bollinger Bands"""
        if price > upper:
            return 'Above Upper Band (Overbought)'
        elif price < lower:
            return 'Below Lower Band (Oversold)'
        else:
            pct = (price - lower) / (upper - lower) * 100
            if pct > 75:
                return 'Upper Region (Strong)'
            elif pct > 25:
                return 'Middle Region (Neutral)'
            else:
                return 'Lower Region (Weak)'
    
    def _generate_overall_signal(self, price: float, sma_50: float, sma_200: float, 
                                 rsi: float, macd_hist: float) -> Dict:
        """Generate overall buy/sell/hold signal"""
        score = 0
        signals = []
        
        # Trend (most important)
        if price > sma_200:
            score += 3
            signals.append('Price above 200-day SMA (Bullish)')
        else:
            score -= 3
            signals.append('Price below 200-day SMA (Bearish)')
        
        # Medium-term trend
        if price > sma_50:
            score += 2
            signals.append('Price above 50-day SMA')
        else:
            score -= 2
            signals.append('Price below 50-day SMA')
        
        # Momentum
        if 30 <= rsi <= 50:
            score += 2
            signals.append('RSI in buy zone')
        elif 50 < rsi < 70:
            score += 1
        elif rsi >= 70:
            score -= 2
            signals.append('RSI overbought')
        elif rsi < 30:
            score += 2
            signals.append('RSI oversold (opportunity)')
        
        # MACD
        if macd_hist > 0:
            score += 1
            signals.append('MACD bullish')
        else:
            score -= 1
            signals.append('MACD bearish')
        
        # Overall
        if score >= 5:
            overall = 'Strong Buy'
        elif score >= 2:
            overall = 'Buy'
        elif score >= -1:
            overall = 'Hold'
        elif score >= -4:
            overall = 'Sell'
        else:
            overall = 'Strong Sell'
        
        return {
            'signal': overall,
            'score': score,
            'factors': signals
        }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def analyze_technical(price_data: pd.DataFrame) -> Dict:
    """
    Main function to run full technical analysis
    
    Args:
        price_data: DataFrame with OHLCV data
        
    Returns:
        Complete technical analysis dictionary
    """
    ta = TechnicalAnalysis(price_data)
    return ta.get_current_signals()


# ============================================================================
# TESTING CODE
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("TESTING TECHNICAL ANALYSIS MODULE")
    print("="*80)
    
    # Test with sample data
    import yfinance as yf
    
    print("\n[TEST] Downloading AAPL data...")
    ticker = yf.Ticker("AAPL")
    hist = ticker.history(period="1y")
    
    if hist.empty:
        print("[FAIL] No data retrieved")
        exit(1)
    
    print(f"[OK] Retrieved {len(hist)} days of data")
    
    print("\n[TEST] Running technical analysis...")
    signals = analyze_technical(hist)
    
    print("\n" + "="*80)
    print("TECHNICAL ANALYSIS RESULTS (AAPL)")
    print("="*80)
    
    print(f"\nCurrent Price: ${signals['price']:.2f}")
    
    print("\n--- MOVING AVERAGES ---")
    ma = signals['moving_averages']
    print(f"SMA 20:  ${ma['sma_20']:.2f} ({ma['price_vs_sma20']})")
    print(f"SMA 50:  ${ma['sma_50']:.2f} ({ma['price_vs_sma50']})")
    print(f"SMA 200: ${ma['sma_200']:.2f} ({ma['price_vs_sma200']})")
    print(f"Golden Cross: {'Yes' if ma['golden_cross'] else 'No'}")
    
    print("\n--- MOMENTUM ---")
    mom = signals['momentum']
    print(f"RSI: {mom['rsi']:.2f} - {mom['rsi_signal']}")
    print(f"MACD: {mom['macd']:.4f}")
    print(f"MACD Signal: {mom['macd_signal']:.4f}")
    print(f"MACD Crossover: {mom['macd_crossover']}")
    
    print("\n--- VOLATILITY ---")
    vol = signals['volatility']
    print(f"ATR: ${vol['atr']:.2f} ({vol['atr_pct']:.2f}% of price)")
    print(f"Bollinger Position: {vol['bb_position']}")
    
    print("\n--- VOLUME ---")
    v = signals['volume']
    print(f"Current Volume: {v['current']:,.0f}")
    print(f"20-day Avg: {v['sma_20']:,.0f}")
    print(f"Relative Volume: {v['relative']}")
    
    print("\n--- SUPPORT & RESISTANCE ---")
    print(f"Resistance: {', '.join([f'${x:.2f}' for x in signals['levels']['resistance']])}")
    print(f"Support: {', '.join([f'${x:.2f}' for x in signals['levels']['support']])}")
    
    print("\n--- OVERALL SIGNAL ---")
    overall = signals['overall_signal']
    print(f"Signal: {overall['signal']} (Score: {overall['score']})")
    print("\nKey Factors:")
    for factor in overall['factors']:
        print(f"  - {factor}")
    
    print("\n" + "="*80)
    print("[SUCCESS] TECHNICAL ANALYSIS TEST COMPLETE")
    print("="*80)





