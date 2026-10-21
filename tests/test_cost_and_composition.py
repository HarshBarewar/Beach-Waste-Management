"""
Tests for Cost Calculation and Waste Composition Estimation.
"""
from backend.app.cost_estimation.calculator import calculate_costs
from backend.app.composition.estimator import estimate_waste_composition

def test_cost_calculation_math():
    waste_kg = 1000.0
    res = calculate_costs(
        total_waste_kg=waste_kg,
        currency="USD",
        collection_cost_per_kg=0.50,
        transport_cost_per_kg=0.20,
        sorting_cost_per_kg=0.10,
        recycling_processing_per_kg=0.30,
        non_recyclable_disposal_per_kg=0.40,
        organic_composting_per_kg=0.15,
        material_revenue_per_kg=0.10,
        fixed_monthly_cost=100.0
    )
    assert res["gross_total_cost"] > res["net_total_cost"]
    assert res["effective_cost_per_kg"] > 0
    assert len(res["materials_cost_breakdown"]) == 6

def test_cost_calculation_currency():
    waste_kg = 1000.0
    res_usd = calculate_costs(waste_kg, currency="USD")
    res_eur = calculate_costs(waste_kg, currency="EUR")
    assert res_eur["currency"] == "EUR"
    # EUR rate is 0.92, so gross cost in EUR should be ~0.92 of USD
    assert abs(res_eur["gross_total_cost"] - res_usd["gross_total_cost"] * 0.92) < 2.0

def test_composition_normalization():
    res = estimate_waste_composition(
        total_waste_kg=2500.0,
        region="North America",
        method="regional_profile"
    )
    total_shares = sum(m["percentage"] for m in res["materials"])
    assert abs(total_shares - 100.0) < 0.2
    assert res["recyclable_kg"] + res["non_recyclable_kg"] + res["biodegradable_kg"] > 2400.0
