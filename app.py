"""Main Streamlit entrypoint."""

import streamlit as st
from typing import Dict
import time

from core.datacenter import DataCenter
from core.powerflow_model import simulate_system, get_solar_ac_dataframe, calculate_energy_mix
from app_components.st_outputs import (
    format_proforma, display_proforma, create_capex_chart, display_intro_section,
    create_energy_mix_chart, display_daily_sample_chart, create_subcategory_capex_charts
)
from app_components.st_inputs import create_system_inputs, calculate_capex_subtotals, create_map_input, create_financial_inputs


def display_capex_breakdown(capex_subtotals: Dict[str, Dict[str, float]]) -> None:
    """Display CAPEX breakdown with metric and chart side by side."""
    st.subheader("CAPEX Breakdown")
    total_capex = sum(component['total_absolute'] for component in capex_subtotals.values())
    st.metric("Total CAPEX", f"${total_capex:.1f}M")
    st.plotly_chart(create_capex_chart(capex_subtotals), use_container_width=True)

    with st.expander("Subcategory breakdown"):
        create_subcategory_capex_charts(capex_subtotals)

def display_energy_mix(energy_mix: Dict[str, float]) -> None:
    """Display energy mix with metric and chart side by side."""
    st.subheader("Energy Mix")
    st.metric("Renewable %", f"{energy_mix['renewable_percentage']:.1f}%")
    st.plotly_chart(create_energy_mix_chart(energy_mix), use_container_width=True)

def main():
    """Main application."""
    display_intro_section()

    run_calculation = st.button(
        "Run calculation",
        type="primary",
        help="Fetch solar data and run the power-flow and financial calculations for the current inputs.",
    )
    st.caption("Change any inputs, then press Run calculation to refresh the results.")

    inputs = create_system_inputs()

    location_col, financial_col = st.columns([1, 1], gap="medium")

    with location_col:
        lat, long, location_name = create_map_input()
        inputs.update({'lat': lat, 'long': long})

    with financial_col:
        financial_inputs = create_financial_inputs(inputs['generator_type'])
        inputs.update(financial_inputs)

    if run_calculation:
        calc_status_display = st.empty()
        st.session_state.calculation_status = (
            f"Selected ({round(lat, 1)}, {round(long, 1)}) in {location_name}\n"
            "Fetching weather data..."
        )
        calc_status_display.code(st.session_state.calculation_status, language="")

        # Fetch weather data only after the user explicitly presses Run calculation.
        t1 = time.time()
        solar_ac_dataframe = get_solar_ac_dataframe(lat, long)
        st.session_state.calculation_status += (
            f"\nWeather data fetched in {time.time()-t1:.2f} seconds"
        )
        calc_status_display.code(st.session_state.calculation_status)

        st.session_state.calculation_status += (
            "\nSimulating solar and battery power flow..."
        )
        calc_status_display.code(st.session_state.calculation_status)

        t1 = time.time()
        powerflow_results = simulate_system(
            inputs['lat'],
            inputs['long'],
            solar_ac_dataframe,
            inputs['solar_pv_capacity_mw'],
            inputs['bess_max_power_mw'],
            inputs['generator_capacity_mw'],
            inputs['datacenter_load_mw'],
        )
        st.session_state.calculation_status += (
            f"\nPowerflow simulation ran in {time.time()-t1:.2f} seconds"
        )
        calc_status_display.code(st.session_state.calculation_status)
        annual_powerflow_results = powerflow_results['annual_results']
        daily_powerflow_results = powerflow_results['daily_sample']
        capex_subtotals = calculate_capex_subtotals(inputs)

        # Create the DataCenter instance to simulate LCOE.
        try:
            data_center = DataCenter(
                solar_pv_capacity_mw=inputs['solar_pv_capacity_mw'],
                bess_max_power_mw=inputs['bess_max_power_mw'],
                generator_capacity_mw=inputs['generator_capacity_mw'],
                generator_type=inputs['generator_type'],
                datacenter_load_mw=inputs['datacenter_load_mw'],
                solar_capex_total_dollar_per_w=capex_subtotals['solar']['rate'],
                bess_capex_total_dollar_per_kwh=capex_subtotals['bess']['rate'],
                generator_capex_total_dollar_per_kw=capex_subtotals['generator']['rate'],
                system_integration_capex_total_dollar_per_kw=capex_subtotals['system_integration']['rate'],
                soft_costs_capex_total_pct=capex_subtotals['soft_costs']['rate'],
                om_solar_fixed_dollar_per_kw=inputs['solar_om_fixed_dollar_per_kw'],
                om_bess_fixed_dollar_per_kw=inputs['bess_om_fixed_dollar_per_kw'],
                om_generator_fixed_dollar_per_kw=inputs['generator_om_fixed_dollar_per_kw'],
                om_generator_variable_dollar_per_kwh=inputs['generator_om_variable_dollar_per_kwh'],
                fuel_price_dollar_per_mmbtu=inputs['fuel_price_dollar_per_mmbtu'],
                fuel_escalator_pct=inputs['fuel_escalator_pct'],
                om_bos_fixed_dollar_per_kw_load=inputs['bos_om_fixed_dollar_per_kw_load'],
                om_soft_pct=inputs['soft_om_pct'],
                om_escalator_pct=inputs['om_escalator_pct'],
                debt_term_years=inputs['debt_term_years'],
                leverage_pct=inputs['leverage_pct'],
                cost_of_debt_pct=inputs['cost_of_debt_pct'],
                cost_of_equity_pct=inputs['cost_of_equity_pct'],
                combined_tax_rate_pct=inputs['combined_tax_rate_pct'],
                investment_tax_credit_pct=inputs['investment_tax_credit_pct'],
                depreciation_schedule=inputs['depreciation_schedule'],
                filtered_simulation_data=annual_powerflow_results
            )
        except ValueError as e:
            st.error(str(e))
            st.stop()

        lcoe, pro_forma = data_center.calculate_lcoe()
        st.session_state.calculation_results = {
            "daily_powerflow_results": daily_powerflow_results,
            "energy_mix": calculate_energy_mix(annual_powerflow_results),
            "capex_subtotals": capex_subtotals,
            "lcoe": lcoe,
            "formatted_proforma": format_proforma(pro_forma),
        }
    elif "calculation_results" not in st.session_state:
        st.info("Set the inputs above, then press Run calculation to fetch data and evaluate the system.")
        return
    else:
        st.warning("Showing the last completed calculation. Press Run calculation to refresh the results for the current inputs.")

    calculation_results = st.session_state.calculation_results

    st.divider()

    # Display the interactive worst-week power flow and energy mix.
    graph_col, energy_mix_col = st.columns([2, 2], gap="medium")
    with graph_col:
        st.subheader("Power Flow (Worst Week)")
        display_daily_sample_chart(calculation_results["daily_powerflow_results"])

    with energy_mix_col:
        display_energy_mix(calculation_results["energy_mix"])

    st.divider()
    display_capex_breakdown(calculation_results["capex_subtotals"])

    st.subheader("Levelized Cost of Electricity")
    st.metric("Calculated LCOE", f"${calculation_results['lcoe']:.2f}/MWh")

    st.subheader("Financial Model")
    display_proforma(calculation_results["formatted_proforma"])

    
if __name__ == "__main__":
    main()
