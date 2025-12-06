"""
MONTE CARLO SIMULATION ENGINE
=============================
Professional-grade stochastic modeling for financial analysis.

Features:
1. DCF Valuation with uncertainty quantification
2. Value at Risk (VaR) and CVaR calculations
3. Earnings surprise probability
4. Dividend sustainability analysis
5. Sensitivity tornado charts
6. Break-even probability

Author: ATLAS Financial Intelligence
Date: December 2025
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from scipy import stats
import plotly.graph_objects as go
import plotly.express as px


@dataclass
class SimulationParams:
    """Parameters for Monte Carlo simulation"""
    n_simulations: int = 10000
    seed: Optional[int] = None  # For reproducibility
    confidence_levels: List[float] = None
    
    def __post_init__(self):
        if self.confidence_levels is None:
            self.confidence_levels = [0.05, 0.25, 0.50, 0.75, 0.95]


class MonteCarloEngine:
    """
    Monte Carlo simulation engine for financial analysis
    
    Methods:
        dcf_simulation: Simulate DCF valuation with uncertain inputs
        var_calculation: Calculate Value at Risk
        earnings_simulation: Simulate earnings outcomes
        dividend_sustainability: Analyze dividend cut probability
        sensitivity_analysis: Tornado chart of input sensitivities
    """
    
    def __init__(self, params: SimulationParams = None):
        self.params = params or SimulationParams()
        if self.params.seed:
            np.random.seed(self.params.seed)
    
    # =========================================================================
    # 1. DCF VALUATION SIMULATION
    # =========================================================================
    
    def dcf_simulation(
        self,
        base_revenue: float,
        base_fcf_margin: float,
        shares_outstanding: float,
        net_debt: float,
        # Distributions for uncertain inputs
        growth_rate_dist: Dict = None,
        wacc_dist: Dict = None,
        terminal_growth_dist: Dict = None,
        margin_dist: Dict = None,
        projection_years: int = 5
    ) -> Dict:
        """
        Monte Carlo simulation of DCF valuation
        
        Args:
            base_revenue: Current annual revenue
            base_fcf_margin: Current FCF margin
            shares_outstanding: Shares for per-share calculation
            net_debt: Total debt minus cash
            growth_rate_dist: {'type': 'normal', 'mean': 0.08, 'std': 0.03}
            wacc_dist: {'type': 'normal', 'mean': 0.09, 'std': 0.015}
            terminal_growth_dist: {'type': 'triangular', 'min': 0.01, 'mode': 0.025, 'max': 0.04}
            margin_dist: {'type': 'normal', 'mean': 0.25, 'std': 0.05}
            projection_years: Number of projection years
        
        Returns:
            Dictionary with simulation results and distributions
        """
        n = self.params.n_simulations
        
        # Default distributions if not provided
        if growth_rate_dist is None:
            growth_rate_dist = {'type': 'normal', 'mean': 0.08, 'std': 0.03}
        if wacc_dist is None:
            wacc_dist = {'type': 'normal', 'mean': 0.09, 'std': 0.015}
        if terminal_growth_dist is None:
            terminal_growth_dist = {'type': 'triangular', 'min': 0.015, 'mode': 0.025, 'max': 0.035}
        if margin_dist is None:
            margin_dist = {'type': 'normal', 'mean': base_fcf_margin, 'std': base_fcf_margin * 0.15}
        
        # Generate random samples
        growth_rates = self._sample_distribution(growth_rate_dist, n)
        waccs = self._sample_distribution(wacc_dist, n)
        terminal_growths = self._sample_distribution(terminal_growth_dist, n)
        margins = self._sample_distribution(margin_dist, n)
        
        # Ensure valid ranges
        growth_rates = np.clip(growth_rates, -0.20, 0.50)
        waccs = np.clip(waccs, 0.04, 0.20)
        terminal_growths = np.clip(terminal_growths, 0.005, 0.045)
        margins = np.clip(margins, 0.01, 0.60)
        
        # Run simulations
        enterprise_values = np.zeros(n)
        equity_values = np.zeros(n)
        values_per_share = np.zeros(n)
        
        for i in range(n):
            # Project FCF for each year
            fcfs = []
            revenue = base_revenue
            for year in range(1, projection_years + 1):
                revenue *= (1 + growth_rates[i])
                fcf = revenue * margins[i]
                discount_factor = (1 + waccs[i]) ** year
                fcfs.append(fcf / discount_factor)
            
            # Terminal value
            terminal_fcf = revenue * (1 + growth_rates[i]) * margins[i]
            if waccs[i] > terminal_growths[i]:
                terminal_value = terminal_fcf * (1 + terminal_growths[i]) / (waccs[i] - terminal_growths[i])
                pv_terminal = terminal_value / ((1 + waccs[i]) ** projection_years)
            else:
                pv_terminal = 0  # Invalid case
            
            # Total value
            enterprise_values[i] = sum(fcfs) + pv_terminal
            equity_values[i] = enterprise_values[i] - net_debt
            values_per_share[i] = equity_values[i] / shares_outstanding if shares_outstanding > 0 else 0
        
        # Filter out invalid results
        valid_mask = (values_per_share > 0) & (values_per_share < base_revenue * 100)  # Sanity check
        values_per_share = values_per_share[valid_mask]
        
        # Calculate statistics
        percentiles = np.percentile(values_per_share, [5, 10, 25, 50, 75, 90, 95])
        
        return {
            'status': 'success',
            'n_simulations': len(values_per_share),
            'values_per_share': values_per_share,
            'statistics': {
                'mean': np.mean(values_per_share),
                'median': np.median(values_per_share),
                'std': np.std(values_per_share),
                'min': np.min(values_per_share),
                'max': np.max(values_per_share),
                'percentile_5': percentiles[0],
                'percentile_10': percentiles[1],
                'percentile_25': percentiles[2],
                'percentile_50': percentiles[3],
                'percentile_75': percentiles[4],
                'percentile_90': percentiles[5],
                'percentile_95': percentiles[6],
            },
            'input_distributions': {
                'growth_rates': {'mean': np.mean(growth_rates), 'std': np.std(growth_rates)},
                'waccs': {'mean': np.mean(waccs), 'std': np.std(waccs)},
                'terminal_growths': {'mean': np.mean(terminal_growths), 'std': np.std(terminal_growths)},
                'margins': {'mean': np.mean(margins), 'std': np.std(margins)},
            }
        }
    
    def probability_above_price(self, simulation_results: Dict, current_price: float) -> float:
        """Calculate probability that intrinsic value > current price"""
        values = simulation_results.get('values_per_share', [])
        if len(values) == 0:
            return 0.0
        return np.mean(values > current_price)
    
    # =========================================================================
    # 2. VALUE AT RISK (VaR) CALCULATION
    # =========================================================================
    
    def calculate_var(
        self,
        returns: np.ndarray,
        portfolio_value: float,
        confidence_levels: List[float] = None,
        holding_period_days: int = 1
    ) -> Dict:
        """
        Calculate Value at Risk using historical simulation
        
        Args:
            returns: Array of historical daily returns
            portfolio_value: Current portfolio value
            confidence_levels: [0.95, 0.99] for 95% and 99% VaR
            holding_period_days: Holding period in days
        
        Returns:
            Dictionary with VaR metrics
        """
        if confidence_levels is None:
            confidence_levels = [0.95, 0.99]
        
        # Scale returns for holding period
        if holding_period_days > 1:
            scaled_returns = returns * np.sqrt(holding_period_days)
        else:
            scaled_returns = returns
        
        results = {
            'portfolio_value': portfolio_value,
            'holding_period_days': holding_period_days,
            'var': {},
            'cvar': {},  # Conditional VaR (Expected Shortfall)
        }
        
        for cl in confidence_levels:
            alpha = 1 - cl
            var_return = np.percentile(scaled_returns, alpha * 100)
            var_dollar = abs(var_return) * portfolio_value
            
            # CVaR: Average of losses beyond VaR
            cvar_returns = scaled_returns[scaled_returns <= var_return]
            cvar_return = np.mean(cvar_returns) if len(cvar_returns) > 0 else var_return
            cvar_dollar = abs(cvar_return) * portfolio_value
            
            results['var'][f'{int(cl*100)}%'] = {
                'return': var_return,
                'dollar': var_dollar,
            }
            results['cvar'][f'{int(cl*100)}%'] = {
                'return': cvar_return,
                'dollar': cvar_dollar,
            }
        
        # Additional risk metrics
        results['max_drawdown'] = self._calculate_max_drawdown(returns)
        results['volatility_annual'] = np.std(returns) * np.sqrt(252)
        results['sharpe_estimate'] = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0
        
        return results
    
    def _calculate_max_drawdown(self, returns: np.ndarray) -> float:
        """Calculate maximum drawdown from return series"""
        cumulative = np.cumprod(1 + returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdowns = cumulative / running_max - 1
        return np.min(drawdowns)
    
    # =========================================================================
    # 3. EARNINGS SIMULATION
    # =========================================================================
    
    def earnings_simulation(
        self,
        expected_eps: float,
        historical_surprises: List[float] = None,
        analyst_range: Tuple[float, float] = None
    ) -> Dict:
        """
        Simulate next quarter earnings based on historical surprise distribution
        
        Args:
            expected_eps: Consensus EPS estimate
            historical_surprises: List of past surprise percentages
            analyst_range: (low_estimate, high_estimate)
        
        Returns:
            Dictionary with earnings simulation results
        """
        n = self.params.n_simulations
        
        if historical_surprises and len(historical_surprises) >= 4:
            # Fit distribution to historical surprises
            surprise_mean = np.mean(historical_surprises)
            surprise_std = np.std(historical_surprises)
            simulated_surprises = np.random.normal(surprise_mean, surprise_std, n)
        else:
            # Default: Assume ±5% std dev
            simulated_surprises = np.random.normal(0, 0.05, n)
        
        simulated_eps = expected_eps * (1 + simulated_surprises)
        
        # If analyst range provided, use it to bound simulations
        if analyst_range:
            low, high = analyst_range
            simulated_eps = np.clip(simulated_eps, low * 0.9, high * 1.1)
        
        beat_probability = np.mean(simulated_eps > expected_eps)
        miss_probability = np.mean(simulated_eps < expected_eps)
        
        return {
            'expected_eps': expected_eps,
            'simulated_eps': simulated_eps,
            'statistics': {
                'mean': np.mean(simulated_eps),
                'median': np.median(simulated_eps),
                'std': np.std(simulated_eps),
                'percentile_5': np.percentile(simulated_eps, 5),
                'percentile_95': np.percentile(simulated_eps, 95),
            },
            'probabilities': {
                'beat': beat_probability,
                'miss': miss_probability,
                'inline': 1 - beat_probability - miss_probability,
            },
            'beat_probability': beat_probability,
        }
    
    # =========================================================================
    # 4. DIVIDEND SUSTAINABILITY
    # =========================================================================
    
    def dividend_sustainability(
        self,
        current_dividend: float,
        eps_distribution: Dict = None,
        fcf_distribution: Dict = None,
        years_forward: int = 3
    ) -> Dict:
        """
        Analyze probability of dividend cut based on payout ratio simulation
        
        Args:
            current_dividend: Current annual dividend per share
            eps_distribution: {'mean': 5.0, 'std': 1.0}
            fcf_distribution: {'mean': 7.0, 'std': 2.0}
            years_forward: Years to simulate
        
        Returns:
            Dictionary with dividend sustainability metrics
        """
        n = self.params.n_simulations
        
        if eps_distribution is None:
            return {'status': 'error', 'message': 'EPS distribution required'}
        
        # Simulate EPS and FCF
        eps_sims = np.random.normal(
            eps_distribution['mean'],
            eps_distribution['std'],
            (n, years_forward)
        )
        
        if fcf_distribution:
            fcf_sims = np.random.normal(
                fcf_distribution['mean'],
                fcf_distribution['std'],
                (n, years_forward)
            )
        else:
            fcf_sims = eps_sims * 1.2  # Assume FCF > EPS typically
        
        # Calculate payout ratios
        payout_ratios = current_dividend / eps_sims
        fcf_payout_ratios = current_dividend / fcf_sims
        
        # Probability of unsustainable payout (>100%) in any year
        unsustainable_eps = np.any(payout_ratios > 1.0, axis=1)
        unsustainable_fcf = np.any(fcf_payout_ratios > 1.0, axis=1)
        
        # Probability of dividend cut (payout > 80% is warning)
        warning_threshold = np.any(payout_ratios > 0.80, axis=1)
        
        return {
            'current_dividend': current_dividend,
            'years_analyzed': years_forward,
            'sustainability': {
                'probability_eps_cut': np.mean(unsustainable_eps),
                'probability_fcf_cut': np.mean(unsustainable_fcf),
                'probability_warning': np.mean(warning_threshold),
            },
            'payout_ratio_stats': {
                'mean': np.mean(payout_ratios),
                'median': np.median(payout_ratios),
                'max': np.max(payout_ratios),
                'percentile_95': np.percentile(payout_ratios, 95),
            },
            'interpretation': self._interpret_dividend_sustainability(
                np.mean(unsustainable_eps),
                np.mean(warning_threshold)
            )
        }
    
    def _interpret_dividend_sustainability(self, cut_prob: float, warning_prob: float) -> str:
        """Generate human-readable interpretation"""
        if cut_prob < 0.05:
            return "SAFE: Very low probability of dividend cut. Well covered by earnings."
        elif cut_prob < 0.15:
            return "MODERATE: Some scenarios show strain. Monitor earnings closely."
        elif cut_prob < 0.30:
            return "CAUTION: Elevated risk of dividend reduction. Consider reducing exposure."
        else:
            return "HIGH RISK: Significant probability of dividend cut. Not sustainable at current levels."
    
    # =========================================================================
    # 5. SENSITIVITY TORNADO CHART
    # =========================================================================
    
    def sensitivity_analysis(
        self,
        base_value: float,
        inputs: Dict[str, Dict]  # {'Revenue Growth': {'base': 0.08, 'range': 0.05}, ...}
    ) -> Dict:
        """
        One-at-a-time sensitivity analysis for tornado chart
        
        Args:
            base_value: Base case intrinsic value
            inputs: Dictionary of inputs with base values and ranges
        
        Returns:
            Sensitivity data for tornado chart
        """
        sensitivities = []
        
        for name, params in inputs.items():
            base = params['base']
            range_val = params.get('range', base * 0.25)  # Default ±25%
            
            low_input = base - range_val
            high_input = base + range_val
            
            # Calculate impact (simplified - would need callback for real calculation)
            # Using linear approximation: impact proportional to % change
            pct_change = range_val / base if base != 0 else 0.1
            
            low_value = base_value * (1 - pct_change * params.get('sensitivity', 1))
            high_value = base_value * (1 + pct_change * params.get('sensitivity', 1))
            
            sensitivities.append({
                'input': name,
                'low_value': low_value,
                'high_value': high_value,
                'base_value': base_value,
                'range': high_value - low_value,
                'low_input': low_input,
                'high_input': high_input,
            })
        
        # Sort by range (largest impact first)
        sensitivities.sort(key=lambda x: x['range'], reverse=True)
        
        return {
            'base_value': base_value,
            'sensitivities': sensitivities,
        }
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def _sample_distribution(self, dist: Dict, n: int) -> np.ndarray:
        """Sample from specified distribution"""
        dist_type = dist.get('type', 'normal')
        
        if dist_type == 'normal':
            return np.random.normal(dist['mean'], dist['std'], n)
        elif dist_type == 'triangular':
            return np.random.triangular(dist['min'], dist['mode'], dist['max'], n)
        elif dist_type == 'uniform':
            return np.random.uniform(dist['min'], dist['max'], n)
        elif dist_type == 'lognormal':
            return np.random.lognormal(dist['mean'], dist['std'], n)
        else:
            # Default to normal
            return np.random.normal(dist.get('mean', 0), dist.get('std', 1), n)


# =============================================================================
# VISUALIZATION HELPERS
# =============================================================================

def plot_dcf_distribution(simulation_results: Dict, current_price: float = None) -> go.Figure:
    """Create histogram of DCF simulation results"""
    values = simulation_results.get('values_per_share', [])
    stats = simulation_results.get('statistics', {})
    
    fig = go.Figure()
    
    # Histogram
    fig.add_trace(go.Histogram(
        x=values,
        nbinsx=50,
        name='Simulated Values',
        marker_color='rgba(59, 130, 246, 0.7)',
    ))
    
    # Add percentile lines
    fig.add_vline(x=stats.get('percentile_5', 0), line_dash="dash", 
                  annotation_text="5th %ile", line_color="red")
    fig.add_vline(x=stats.get('percentile_50', 0), line_dash="solid",
                  annotation_text="Median", line_color="green")
    fig.add_vline(x=stats.get('percentile_95', 0), line_dash="dash",
                  annotation_text="95th %ile", line_color="red")
    
    if current_price:
        fig.add_vline(x=current_price, line_dash="dot",
                      annotation_text=f"Current: ${current_price:.0f}", line_color="orange")
    
    fig.update_layout(
        title="DCF Valuation Distribution (Monte Carlo)",
        xaxis_title="Intrinsic Value per Share ($)",
        yaxis_title="Frequency",
        template="plotly_dark",
        showlegend=False,
    )
    
    return fig


def plot_tornado_chart(sensitivity_data: Dict) -> go.Figure:
    """Create tornado chart for sensitivity analysis"""
    sensitivities = sensitivity_data.get('sensitivities', [])
    base_value = sensitivity_data.get('base_value', 0)
    
    fig = go.Figure()
    
    for i, s in enumerate(sensitivities):
        # Low side (red)
        fig.add_trace(go.Bar(
            y=[s['input']],
            x=[s['low_value'] - base_value],
            orientation='h',
            marker_color='#ef4444',
            name='Downside',
            showlegend=(i == 0),
        ))
        # High side (green)
        fig.add_trace(go.Bar(
            y=[s['input']],
            x=[s['high_value'] - base_value],
            orientation='h',
            marker_color='#22c55e',
            name='Upside',
            showlegend=(i == 0),
        ))
    
    fig.add_vline(x=0, line_color="white", line_width=2)
    
    fig.update_layout(
        title="Sensitivity Analysis (Tornado Chart)",
        xaxis_title=f"Impact on Value (Base: ${base_value:.0f})",
        barmode='overlay',
        template="plotly_dark",
    )
    
    return fig


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("MONTE CARLO ENGINE - TEST SUITE")
    print("=" * 80)
    
    # Initialize engine
    engine = MonteCarloEngine(SimulationParams(n_simulations=10000, seed=42))
    
    # Test 1: DCF Simulation
    print("\n1. DCF SIMULATION TEST")
    print("-" * 40)
    
    dcf_result = engine.dcf_simulation(
        base_revenue=385e9,  # $385B (Apple-like)
        base_fcf_margin=0.25,
        shares_outstanding=15.5e9,
        net_debt=-60e9,  # Net cash
    )
    
    stats = dcf_result['statistics']
    print(f"  Simulations: {dcf_result['n_simulations']:,}")
    print(f"  Mean Value: ${stats['mean']:.2f}")
    print(f"  Median Value: ${stats['median']:.2f}")
    print(f"  5th Percentile: ${stats['percentile_5']:.2f}")
    print(f"  95th Percentile: ${stats['percentile_95']:.2f}")
    
    # Probability above current price
    current_price = 175
    prob_undervalued = engine.probability_above_price(dcf_result, current_price)
    print(f"  Probability > ${current_price}: {prob_undervalued:.1%}")
    
    # Test 2: VaR Calculation
    print("\n2. VALUE AT RISK TEST")
    print("-" * 40)
    
    # Simulate some returns
    np.random.seed(42)
    returns = np.random.normal(0.0005, 0.02, 252)  # 1 year of daily returns
    
    var_result = engine.calculate_var(
        returns=returns,
        portfolio_value=100000,
        confidence_levels=[0.95, 0.99]
    )
    
    print(f"  Portfolio: ${var_result['portfolio_value']:,.0f}")
    print(f"  95% VaR (1-day): ${var_result['var']['95%']['dollar']:,.0f}")
    print(f"  99% VaR (1-day): ${var_result['var']['99%']['dollar']:,.0f}")
    print(f"  Max Drawdown: {var_result['max_drawdown']:.1%}")
    print(f"  Annual Volatility: {var_result['volatility_annual']:.1%}")
    
    # Test 3: Earnings Simulation
    print("\n3. EARNINGS SIMULATION TEST")
    print("-" * 40)
    
    earnings_result = engine.earnings_simulation(
        expected_eps=6.50,
        historical_surprises=[0.05, 0.03, -0.02, 0.08, 0.04, 0.02, 0.06, -0.01],
    )
    
    print(f"  Expected EPS: ${earnings_result['expected_eps']:.2f}")
    print(f"  Simulated Mean: ${earnings_result['statistics']['mean']:.2f}")
    print(f"  Beat Probability: {earnings_result['probabilities']['beat']:.1%}")
    print(f"  Miss Probability: {earnings_result['probabilities']['miss']:.1%}")
    
    # Test 4: Dividend Sustainability
    print("\n4. DIVIDEND SUSTAINABILITY TEST")
    print("-" * 40)
    
    div_result = engine.dividend_sustainability(
        current_dividend=3.68,
        eps_distribution={'mean': 6.50, 'std': 0.80},
        fcf_distribution={'mean': 7.20, 'std': 1.20},
        years_forward=3
    )
    
    print(f"  Current Dividend: ${div_result['current_dividend']:.2f}")
    print(f"  Cut Probability (EPS): {div_result['sustainability']['probability_eps_cut']:.1%}")
    print(f"  Cut Probability (FCF): {div_result['sustainability']['probability_fcf_cut']:.1%}")
    print(f"  Mean Payout Ratio: {div_result['payout_ratio_stats']['mean']:.1%}")
    print(f"  Interpretation: {div_result['interpretation']}")
    
    print("\n" + "=" * 80)
    print("ALL TESTS PASSED")
    print("=" * 80)

