"""Quick Monte Carlo test"""
from monte_carlo_engine import MonteCarloEngine, SimulationParams

# Initialize
e = MonteCarloEngine(SimulationParams(n_simulations=1000, seed=42))

# Run DCF simulation (Apple-like company)
r = e.dcf_simulation(
    base_revenue=385e9,
    base_fcf_margin=0.25,
    shares_outstanding=15.5e9,
    net_debt=-60e9  # Net cash
)

print("=" * 50)
print("MONTE CARLO DCF SIMULATION")
print("=" * 50)
print(f"Simulations: {r['n_simulations']}")
print(f"Median Value: ${r['statistics']['median']:.2f}")
print(f"Mean Value: ${r['statistics']['mean']:.2f}")
print(f"5th Percentile: ${r['statistics']['percentile_5']:.2f}")
print(f"95th Percentile: ${r['statistics']['percentile_95']:.2f}")

# Probability above current price
current_price = 175
prob = e.probability_above_price(r, current_price)
print(f"\nProbability > ${current_price}: {prob:.1%}")
print("=" * 50)

