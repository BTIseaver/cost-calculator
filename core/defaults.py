"""Default values for all inputs used in the LCOE calculator."""

SIMULATION_DATA_PATH = 'data/powerflow_output_frozen.csv'

DATACENTER_DEMAND_MW = 100
BESS_HRS_STORAGE = 4

# Generator heat rates
GENERATOR_HEAT_RATES = {
    'Gas Engine': 8989,  # BTU/kWh
    'Gas Turbine': 9630  # BTU/kWh
}

# Generator costs
DEFAULTS_GENERATORS = {
    'Gas Engine': {
        'capex': {
            'gensets': 800,
            'balance_of_system': 200,
            'labor': 150
        },
        'opex': {
            'fixed_om': 10.00,
            'variable_om': 0.025
        }
    },
    'Gas Turbine': {
        'capex': {
            'gensets': 635,
            'balance_of_system': 150,
            'labor': 100
        },
        'opex': {
            'fixed_om': 15.00,
            'variable_om': 0.005
        }
    }
}

DEFAULTS_DATACENTER_LOAD = [50, 100, 200, 500, 1000]

# Solar PV CAPEX defaults ($/W)
DEFAULTS_SOLAR_CAPEX = {
    'modules': 0.220,
    'inverters': 0.050,
    'racking': 0.180,
    'balance_of_system': 0.120,
    'labor': 0.200
}

# BESS CAPEX defaults ($/kWh)
DEFAULTS_BESS_CAPEX = {
    'units': 200,
    'balance_of_system': 40,
    'labor': 20
}

# System Integration CAPEX defaults ($/kW)
DEFAULTS_SYSTEM_INTEGRATION_CAPEX = {
    'microgrid': 300,
    'controls': 50,
    'labor': 60
}

# Soft Costs defaults (%)
DEFAULTS_SOFT_COSTS_CAPEX = {
    'general_conditions': 0.50,
    'epc_overhead': 5.00,
    'design_engineering': 0.50,
    'permitting': 0.05,
    'startup': 0.25,
    'insurance': 0.50,
    'taxes': 0.00
}

DEFAULTS_OM = {
    'fuel_price_dollar_per_mmbtu': 5.00,
    'fuel_escalator_pct': 3.00,
    'solar_fixed_dollar_per_kw': 11,
    'bess_fixed_dollar_per_kw': 2.5,
    'bos_fixed_dollar_per_kw_load': 6.0,
    'soft_pct': 0.25,
    'escalator_pct': 2.50
}

DEFAULTS_FINANCIAL = {
    'cost_of_debt_pct': 7.5,
    'leverage_pct': 70.0,
    'debt_term_years': 20,
    'cost_of_equity_pct': 11.0,
    'investment_tax_credit_pct': 0.0,
    'combined_tax_rate_pct': 0.0,
    'construction_time_years': 2
}

# Default MACRS depreciation schedule
DEFAULTS_DEPRECIATION_SCHEDULE = [
    20.0,   # Year 1
    32.0,   # Year 2
    19.20,  # Year 3
    11.52,  # Year 4
    11.52,  # Year 5
    5.76,   # Year 6
    0.0,    # Year 7-20
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0
]
