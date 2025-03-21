# -*- coding: utf-8 -*-
"""Problem Set 1.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1kVVZUBiSZNccndmknAOLZD5n5GEy34-E
"""

#3b.
import numpy as np
import pandas as pd

def rouwenhorst(n, rho, sigma):
    """
    Constructs the transition matrix and state space for an AR(1) process using Rouwenhorst's method.

    """
    p = (1 + rho) / 2
    q = p
    Pi = np.array([[p, 1 - p], [1 - q, q]])

    for i in range(2, n):
        Pi_new = np.zeros((i + 1, i + 1))
        Pi_new[:-1, :-1] += p * Pi
        Pi_new[:-1, 1:] += (1 - p) * Pi
        Pi_new[1:, :-1] += (1 - q) * Pi
        Pi_new[1:, 1:] += q * Pi
        Pi_new[1:-1, :] /= 2
        Pi = Pi_new

    s = np.sqrt((sigma ** 2) / (1 - rho ** 2))  # Long-run standard deviation
    z = np.linspace(-s, s, n)  # Discretized state space

    return Pi, z

# Parameters for part (b)
n_states = 7
rho = 0.85
sigma = 1   # SD of white noise

P, z = rouwenhorst(n_states, rho, sigma)


df_transition = pd.DataFrame(P, index=np.round(z, 2), columns=np.round(z, 2))
df_states = pd.DataFrame({'State Values': np.round(z, 2)})


print("\n=== Transition Matrix ===")
print(df_transition)

print("\n=== State Vector ===")
print(df_states)

# Validate the transition matrix sums
print("\nRow Sums (should be all 1s):\n", P.sum(axis=1))

#3c
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from numpy.random import uniform


def simulate(grid, pmat, T, seed=None):
    """
    Simulates the Markov chain.
    """
    N = grid.shape[1]  # Number of states.
    if seed is not None:
        np.random.seed(seed)

    pi0 = np.cumsum(np.ones(N) / N)  # CDF for uniform distribution
    init = np.linspace(0, N-1, N, endpoint=True)  # State indices
    state0 = int(init[uniform() <= pi0][0])  # Initial state

    cmat = np.cumsum(pmat, axis=1)  # CDF matrix
    y = np.zeros((grid.shape[0], T*2))  # Container

    for i in range(0, T*2):  # Simulation
        y[:, i] = grid[:, state0]  # Current state
        state1 = cmat[state0, uniform() <= cmat[state0, :]]  # Next state
        state0 = np.nonzero(cmat[state0, :] == state1[0])[0][0]  # Update state index

    y = y[:, T:T*2]  # Burn-in phase

    return y

# Parameters for simulation
n_states = 7
rho = 0.85
sigma = 1

# Compute state space and transition matrix
grid, P = rouwenhorst(n_states, rho, sigma)

# Convert to 2D array for compatibility
grid = grid.reshape(1, -1)

# Simulate for part (c) with seed 2025
T = 50  # Simulate for 50 periods
seed = 2025
simulated_data = simulate(grid, P, T, seed)

# Plot results for part (c)
plt.figure(figsize=(10, 6))
plt.plot(simulated_data.T, label='Simulation for γ=0.85')
plt.title('Simulated AR(1) Process for γ=0.85 (50 periods)')
plt.xlabel('Time')
plt.ylabel('Value of AR(1) Process')
plt.legend()
plt.grid(True)
plt.show()

# Part 3 (d): Repeat simulation for different γ values
gamma_values = [0.75, 0.95, 0.99]
plt.figure(figsize=(10, 6))

for gamma in gamma_values:
    grid, P = rouwenhorst(n_states, gamma, sigma)
    grid = grid.reshape(1, -1)
    simulated_data = simulate(grid, P, T, seed)
    plt.plot(simulated_data.T, label=f'γ={gamma}')

plt.title('Simulated AR(1) Process for Different γ Values (50 periods)')
plt.xlabel('Time')
plt.ylabel('Value of AR(1) Process')
plt.legend()
plt.grid(True)
plt.show()

#Question 5(d):
import numpy as np
import matplotlib.pyplot as plt

# Parameters
alpha = 0.3  # Capital share in output
beta = 0.96  # Discount factor
delta = 0.1  # Depreciation rate of capital
delta_h = 0.05  # Depreciation rate of human capital
eta = 0.1  # Effectiveness of education investment in increasing human capital
sigma = 0.02  # Standard deviation of the shock
A_0 = 1  # Initial total factor productivity
sigma_eps = 0.07  # Std. dev of productivity shocks
rho = 0.85  # Persistence of AR(1) process

# Time horizon and periods
T = 100  # Time periods
initial_k = 1  # Initial capital stock
initial_h = 1  # Initial human capital

# Stochastic shock for productivity (random walk with normal distribution)
np.random.seed(42)  # For reproducibility
shocks = np.random.normal(0, sigma_eps, T)

# Arrays to store results
k = np.zeros(T)
h = np.zeros(T)
A = np.zeros(T)
output = np.zeros(T)  # Output

# Initial values
k[0] = initial_k
h[0] = initial_h
A[0] = A_0

# Investment in capital and education (for simplicity, assume a fixed investment strategy)
investment_in_education = 0.1  # Fixed investment ratio in education
investment_in_capital = 0.2  # Fixed investment ratio in capital

# Simulate the model
for t in range(1, T):
    # Update productivity based on shock
    A[t] = A[t-1] * (1 + shocks[t])

    # Ensure A[t] does not fall below 0 (avoid negative productivity)
    A[t] = max(A[t], 1e-6)

    # Capital and human capital accumulation
    k[t] = (1 - delta) * k[t-1] + investment_in_capital * A[t] * k[t-1]**alpha * h[t-1]**(1-alpha)
    h[t] = (1 - delta_h) * h[t-1] + eta * investment_in_education * A[t] * k[t-1]**alpha * h[t-1]**(1-alpha)

    # Ensure k[t] and h[t] do not become negative or zero (avoid unrealistic growth)
    k[t] = max(k[t], 1e-6)
    h[t] = max(h[t], 1e-6)

    # Store output
    output[t] = A[t] * k[t]**alpha * h[t]**(1-alpha)

# Plot the results
plt.figure(figsize=(12, 6))

# Plot capital over time
plt.subplot(1, 2, 1)
plt.plot(range(T), k, label="Capital (k)", color="blue")
plt.title("Capital Accumulation Over Time")
plt.xlabel("Time Periods")
plt.ylabel("Capital (k)")
plt.grid(True)

# Plot human capital over time
plt.subplot(1, 2, 2)
plt.plot(range(T), h, label="Human Capital (h)", color="green")
plt.title("Human Capital Accumulation Over Time")
plt.xlabel("Time Periods")
plt.ylabel("Human Capital (h)")
plt.grid(True)

plt.tight_layout()
plt.show()

# Plot Output (Y_t)
plt.figure(figsize=(8, 5))
plt.plot(range(T), output, label="Output (Y_t)", color="orange")
plt.title("Output Over Time (Effect of Education on Growth)")
plt.xlabel("Time Periods")
plt.ylabel("Output (Y_t)")
plt.grid(True)
plt.show()

# Final output calculation
final_output = A[-1] * k[-1]**alpha * h[-1]**(1-alpha)
print(f"Final Output: {final_output:.2f}")

#Question 5(e):
import numpy as np
import matplotlib.pyplot as plt

# Parameters (unchanged)
alpha = 0.3  # Capital share in output
beta = 0.96  # Discount factor
delta = 0.1  # Depreciation rate of capital
delta_h = 0.05  # Depreciation rate of human capital
sigma = 0.02  # Standard deviation of the shock
A_0 = 1  # Initial total factor productivity
sigma_eps = 0.07  # Std. dev of productivity shocks
rho = 0.85  # Persistence of AR(1) process

# Time horizon and periods
T = 100  # Time periods
initial_k = 1  # Initial capital stock
initial_h = 1  # Initial human capital

# Stochastic shock for productivity (random walk with normal distribution)
np.random.seed(42)  # For reproducibility
shocks = np.random.normal(0, sigma_eps, T)

# Arrays to store results for both baseline and policy scenario
k_baseline = np.zeros(T)
h_baseline = np.zeros(T)
output_baseline = np.zeros(T)

k_policy = np.zeros(T)
h_policy = np.zeros(T)
output_policy = np.zeros(T)

# Initial values
k_baseline[0] = initial_k
h_baseline[0] = initial_h
k_policy[0] = initial_k
h_policy[0] = initial_h
A_baseline = A_0
A_policy = A_0

# Baseline scenario: eta = 0.1 (education investment)
eta_baseline = 0.1  # Fixed investment ratio in education

# Policy scenario: eta = 0.2 (education investment doubled)
eta_policy = 0.2  # Policy scenario, education investment doubled

# Simulate the model for baseline scenario
for t in range(1, T):
    A_baseline = A_baseline * (1 + shocks[t])
    A_baseline = max(A_baseline, 1e-6)

    k_baseline[t] = (1 - delta) * k_baseline[t-1] + 0.2 * A_baseline * k_baseline[t-1]**alpha * h_baseline[t-1]**(1-alpha)
    h_baseline[t] = (1 - delta_h) * h_baseline[t-1] + eta_baseline * 0.1 * A_baseline * k_baseline[t-1]**alpha * h_baseline[t-1]**(1-alpha)

    k_baseline[t] = max(k_baseline[t], 1e-6)
    h_baseline[t] = max(h_baseline[t], 1e-6)

    output_baseline[t] = A_baseline * k_baseline[t]**alpha * h_baseline[t]**(1-alpha)

# Simulate the model for policy scenario (double education investment)
for t in range(1, T):
    A_policy = A_policy * (1 + shocks[t])
    A_policy = max(A_policy, 1e-6)

    k_policy[t] = (1 - delta) * k_policy[t-1] + 0.2 * A_policy * k_policy[t-1]**alpha * h_policy[t-1]**(1-alpha)
    h_policy[t] = (1 - delta_h) * h_policy[t-1] + eta_policy * 0.1 * A_policy * k_policy[t-1]**alpha * h_policy[t-1]**(1-alpha)

    k_policy[t] = max(k_policy[t], 1e-6)
    h_policy[t] = max(h_policy[t], 1e-6)

    output_policy[t] = A_policy * k_policy[t]**alpha * h_policy[t]**(1-alpha)

# Plot the results
plt.figure(figsize=(12, 6))

# Plot capital over time (Baseline vs Policy)
plt.subplot(1, 2, 1)
plt.plot(range(T), k_baseline, label="Capital (Baseline)", color="blue")
plt.plot(range(T), k_policy, label="Capital (Policy)", color="orange")
plt.title("Capital Accumulation Over Time")
plt.xlabel("Time Periods")
plt.ylabel("Capital (k)")
plt.legend()
plt.grid(True)

# Plot human capital over time (Baseline vs Policy)
plt.subplot(1, 2, 2)
plt.plot(range(T), h_baseline, label="Human Capital (Baseline)", color="green")
plt.plot(range(T), h_policy, label="Human Capital (Policy)", color="red")
plt.title("Human Capital Accumulation Over Time")
plt.xlabel("Time Periods")
plt.ylabel("Human Capital (h)")
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()

# Plot Output (Y_t) for Baseline vs Policy
plt.figure(figsize=(8, 5))
plt.plot(range(T), output_baseline, label="Output (Baseline)", color="blue")
plt.plot(range(T), output_policy, label="Output (Policy)", color="orange")
plt.title("Output Over Time (Effect of Education Investment Policy)")
plt.xlabel("Time Periods")
plt.ylabel("Output (Y_t)")
plt.legend()
plt.grid(True)
plt.show()

# Final output comparison
final_output_baseline = A_baseline * k_baseline[-1]**alpha * h_baseline[-1]**(1-alpha)
final_output_policy = A_policy * k_policy[-1]**alpha * h_policy[-1]**(1-alpha)