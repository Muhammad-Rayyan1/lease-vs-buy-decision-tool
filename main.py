import streamlit as st
import pandas as pd
from datetime import datetime
import io

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="Lease vs Buy – Fauji Foods Impact Analysis",
    page_icon="📊",
    layout="wide"
)

# ==============================
# TITLE
# ==============================
st.title("Lease vs Buy Decision Impact – Fauji Foods Limited")
st.caption("Strategic Financial Analysis | Pakistan | IFRS-16 & Income Tax Ordinance 2001")

# ==============================
# INTRODUCTION
# ==============================
st.header("🏢 About Fauji Foods Limited")

st.markdown("""
**Fauji Foods Limited (FFL)** is a subsidiary of the **Fauji Foundation Group** and operates in Pakistan’s
**dairy and packaged foods sector**. The company focuses on affordability, nutrition, and long-term
sustainability while adhering to **IFRS reporting standards**.

This project evaluates a **Lease vs Buy capital investment decision** and its impact on:
- Cash flows  
- Profitability  
- Balance sheet structure  
- Shareholder value
""")

st.markdown("---")

# ==============================
# BASELINE FINANCIALS (PKR million)
# ==============================
BASE_ASSETS = 160000
BASE_LIABILITIES = 95000
BASE_EQUITY = 65000
BASE_EBIT = 18000
BASE_NET_PROFIT = 9500
BASE_DEBT = 70000

# ==============================
# HELPER FUNCTIONS
# ==============================
def calculate_npv(rate, cash_flows):
    return sum(cf / ((1 + rate) ** i) for i, cf in enumerate(cash_flows))

def fmt(x):
    return f"₨{x:,.2f} M"

# ==============================
# SIDEBAR INPUTS
# ==============================
with st.sidebar:
    st.header("🔧 Model Inputs")

    tax_rate = st.number_input("Corporate Tax Rate (%)", value=29.0) / 100
    discount_rate = st.number_input("Discount Rate (%)", value=12.0) / 100

    st.subheader("📦 Asset Details")
    purchase_price = st.number_input("Machine Cost (PKR million)", value=100.0)
    useful_life = st.number_input("Useful Life (years)", value=7, min_value=1)
    residual_value = st.number_input("Residual Value (PKR million)", value=15.0)
    maintenance = st.number_input("Annual Maintenance (PKR million)", value=2.0)

    st.subheader("💳 Purchase Mode")
    purchase_mode = st.radio("Machine Purchased Through:", ["Cash", "Credit"])
    interest_rate = 0.0
    if purchase_mode == "Credit":
        interest_rate = st.number_input("Interest Rate (%)", value=14.0) / 100

    st.subheader("📜 Lease Terms")
    lease_payment = st.number_input("Annual Lease Payment (PKR million)", value=18.0)
    maintenance_included = st.checkbox("Maintenance Included in Lease?", True)

# ==============================
# BUY OPTION CASH FLOWS
# ==============================
depreciation = (purchase_price - residual_value) / useful_life
dep_tax_shield = depreciation * tax_rate

buy_cash_flows = [-purchase_price]
for _ in range(useful_life):
    interest_expense = purchase_price * interest_rate if purchase_mode == "Credit" else 0
    cf = dep_tax_shield - maintenance * (1 - tax_rate) - interest_expense * (1 - tax_rate)
    buy_cash_flows.append(cf)

buy_cash_flows[-1] += residual_value
npv_buy = calculate_npv(discount_rate, buy_cash_flows)

# ==============================
# LEASE OPTION CASH FLOWS
# ==============================
lease_cash_flows = [0]
for _ in range(useful_life):
    cf = -lease_payment * (1 - tax_rate)
    if not maintenance_included:
        cf += -maintenance * (1 - tax_rate)
    lease_cash_flows.append(cf)

npv_lease = calculate_npv(discount_rate, lease_cash_flows)
nal = npv_buy - npv_lease

# ==============================
# PREDEFINED SCENARIOS
# ==============================
SCENARIOS = {
    "Production Line Equipment": {
        "description": """**Production Line Equipment Analysis**
        
Create a comprehensive lease vs buy analysis for a new corn flakes production line worth PKR 150 million. 
Include: upfront costs, monthly lease payments of PKR 2.5 million over 5 years, depreciation benefits 
(15% declining balance), tax shields at 29% corporate tax rate, maintenance costs (3% annually for owned, 
included in lease), salvage value (20% after 5 years), and opportunity cost of capital at 15%. 
Present NPV comparison and break-even analysis.""",
        "params": {
            "purchase_price": 150.0,
            "useful_life": 5,
            "residual_value": 30.0,  # 20% salvage
            "maintenance": 4.5,  # 3% annually
            "lease_payment": 30.0,  # 2.5M monthly * 12
            "discount_rate": 15.0,
            "tax_rate": 29.0,
            "depreciation_method": "Declining Balance (15%)"
        }
    },
    "Packaging Machinery": {
        "description": """**Packaging Machinery Decision**
        
Analyze whether Fauji Foods should lease or purchase automated packaging equipment for PKR 45 million. 
Compare: 4-year lease at PKR 1.2 million/month vs purchase with 20% down payment and bank financing at 
18% KIBOR+3%. Include technological obsolescence risk (equipment may be outdated in 3 years), production 
capacity utilization (currently 65%), and flexibility to upgrade. Provide recommendation with sensitivity analysis.""",
        "params": {
            "purchase_price": 45.0,
            "useful_life": 4,
            "residual_value": 9.0,  # 20% after 4 years
            "maintenance": 1.35,  # 3% annually
            "lease_payment": 14.4,  # 1.2M monthly * 12
            "discount_rate": 21.0,  # 18% + 3%
            "tax_rate": 29.0,
            "down_payment": 9.0,  # 20%
            "capacity_utilization": 65
        }
    },
    "Cold Storage Equipment": {
        "description": """**Cold Storage Equipment**
        
Evaluate lease vs buy for cold storage refrigeration units (PKR 80 million). Consider: energy efficiency 
improvements every 2 years, maintenance complexity, regulatory compliance costs, lease terms of 6 years at 
PKR 1.4 million/month, and potential government subsidies for owned energy-efficient equipment (15% subsidy). 
Calculate total cost of ownership vs leasing over 10-year horizon.""",
        "params": {
            "purchase_price": 80.0,
            "useful_life": 10,
            "residual_value": 16.0,  # 20% salvage
            "maintenance": 2.4,  # 3% annually
            "lease_payment": 16.8,  # 1.4M monthly * 12
            "discount_rate": 12.0,
            "tax_rate": 29.0,
            "government_subsidy": 12.0,  # 15% subsidy
            "lease_term": 6
        }
    },
    "Distribution Truck Fleet": {
        "description": """**Distribution Truck Fleet**
        
Create a decision model for 25 distribution trucks (PKR 8 million each). Compare: operating lease vs 
finance lease vs outright purchase. Include fuel costs (PKR 180/liter, 6 km/liter), driver salaries, 
insurance (4% of vehicle value), maintenance (owned: PKR 15,000/month/truck, leased: included), resale 
value depreciation (30% year 1, 15% year 2-5), and working capital impact. Show monthly cash flow comparison.""",
        "params": {
            "purchase_price": 200.0,  # 25 trucks * 8M
            "useful_life": 5,
            "residual_value": 64.0,  # After depreciation
            "maintenance": 4.5,  # 15K/month/truck * 12 * 25 trucks
            "lease_payment": 48.0,  # Estimated
            "discount_rate": 12.0,
            "tax_rate": 29.0,
            "insurance": 8.0,  # 4% of value
            "fuel_cost_annual": 27.0  # Estimated
        }
    },
    "Refrigerated Transport": {
        "description": """**Refrigerated Transport Vehicles**
        
Analyze lease vs buy for 10 refrigerated trucks (PKR 12 million each) for cold chain distribution. 
Consider: specialized maintenance requirements, technological upgrades for GPS tracking and temperature 
monitoring, lease options (full-service vs dry lease), fuel efficiency improvements in newer models, and 
expansion plans for 15 more trucks in year 3. Recommend optimal financing mix.""",
        "params": {
            "purchase_price": 120.0,  # 10 trucks * 12M
            "useful_life": 7,
            "residual_value": 36.0,  # 30% salvage
            "maintenance": 7.2,  # Higher for refrigerated
            "lease_payment": 30.0,  # Full service lease
            "discount_rate": 12.0,
            "tax_rate": 29.0,
            "gps_upgrade": 2.0,
            "expansion_year_3": 180.0  # 15 trucks * 12M
        }
    },
    "Warehouse Facility": {
        "description": """**Warehouse Facility Decision**
        
Evaluate leasing vs purchasing a 100,000 sq ft warehouse in Lahore. Purchase price: PKR 400 million, 
lease: PKR 250/sq ft/month. Include: property appreciation (8% annually), renovation costs (PKR 50 million 
for owned, landlord's responsibility for leased), tax benefits of mortgage interest, flexibility for business 
expansion/contraction, and alternative investment returns. Provide 15-year comparative analysis.""",
        "params": {
            "purchase_price": 400.0,
            "useful_life": 15,
            "residual_value": 1268.0,  # With 8% appreciation
            "maintenance": 8.0,  # Annual maintenance
            "lease_payment": 300.0,  # 250 * 100K sq ft / 12 * 12
            "discount_rate": 12.0,
            "tax_rate": 29.0,
            "renovation": 50.0,
            "appreciation_rate": 8.0
        }
    },
    "Retail Outlet Expansion": {
        "description": """**Retail Outlet Expansion**
        
Analyze lease vs buy decisions for 20 new retail outlets across Pakistan. Average purchase cost: PKR 25 
million/outlet, lease: PKR 350,000/month. Consider: location-specific factors, lease escalation clauses 
(10% every 3 years), exit flexibility if outlet underperforms, working capital preservation for inventory, 
and brand presence strategy. Create a decision matrix with city-wise recommendations.""",
        "params": {
            "purchase_price": 500.0,  # 20 outlets * 25M
            "useful_life": 10,
            "residual_value": 350.0,  # 70% retention
            "maintenance": 10.0,
            "lease_payment": 84.0,  # 350K * 20 * 12
            "discount_rate": 12.0,
            "tax_rate": 29.0,
            "lease_escalation": 10.0,  # Every 3 years
            "working_capital_saved": 100.0
        }
    },
    "Factory Land Acquisition": {
        "description": """**Factory Land Acquisition**
        
Should Fauji Foods lease or buy 50 acres of industrial land for new production facility in Hattar 
Industrial Estate? Purchase: PKR 500 million, lease: PKR 4 million/month (20-year lease). Include: land 
appreciation potential, regulatory requirements for owned land, lease renewal risks, expansion possibilities, 
and collateral value for future financing. Provide strategic recommendation.""",
        "params": {
            "purchase_price": 500.0,
            "useful_life": 20,
            "residual_value": 1165.0,  # With appreciation
            "maintenance": 5.0,  # Land maintenance
            "lease_payment": 48.0,  # 4M * 12
            "discount_rate": 12.0,
            "tax_rate": 29.0,
            "appreciation_rate": 4.5,
            "collateral_value": 500.0
        }
    },
    "ERP System": {
        "description": """**ERP System Implementation**
        
Compare purchasing perpetual licenses vs SaaS subscription for SAP ERP system. Perpetual license: PKR 120 
million upfront + 18% annual maintenance, SaaS: PKR 2.5 million/month. Include: implementation costs, 
upgrade flexibility, scalability for 30% business growth, IT staff requirements, data security considerations, 
and vendor lock-in risks. Calculate 7-year TCO comparison.""",
        "params": {
            "purchase_price": 120.0,
            "useful_life": 7,
            "residual_value": 0.0,  # Software has no salvage
            "maintenance": 21.6,  # 18% annually
            "lease_payment": 30.0,  # 2.5M * 12 (SaaS)
            "discount_rate": 12.0,
            "tax_rate": 29.0,
            "implementation_cost": 25.0,
            "scalability_factor": 30.0
        }
    },
    "Solar Power System": {
        "description": """**Solar Power System**
        
Analyze lease vs buy for 1.5 MW rooftop solar installation at manufacturing plant. Purchase cost: PKR 180 
million (with 30% AEDB subsidy), lease: PKR 2.2 million/month for 15 years. Include: current electricity 
costs (PKR 3.5 million/month), tariff increase projections (12% annually), maintenance, panel degradation, 
net metering benefits, and carbon credit potential. Show payback period for each option.""",
        "params": {
            "purchase_price": 180.0,
            "useful_life": 15,
            "residual_value": 18.0,  # 10% salvage
            "maintenance": 3.6,  # 2% annually
            "lease_payment": 26.4,  # 2.2M * 12
            "discount_rate": 12.0,
            "tax_rate": 29.0,
            "aedb_subsidy": 54.0,  # 30% subsidy
            "electricity_savings": 42.0,  # 3.5M * 12
            "tariff_increase": 12.0
        }
    },
    "Multi-Asset Portfolio": {
        "description": """**Multi-Asset Portfolio Analyzer**
        
Create a comprehensive lease vs buy analyzer for Fauji Foods' annual capital expenditure plan (PKR 500 million 
across 15 different assets). Include: weighted average cost of capital (WACC), debt capacity constraints, 
working capital impact, tax optimization strategy, asset life cycles, and strategic importance ranking. 
Generate an optimal lease-buy mix recommendation.""",
        "params": {
            "purchase_price": 500.0,  # Total portfolio
            "useful_life": 8,  # Average life
            "residual_value": 75.0,  # 15% average salvage
            "maintenance": 15.0,  # 3% annually
            "lease_payment": 90.0,  # Portfolio lease cost
            "discount_rate": 13.5,  # WACC
            "tax_rate": 29.0,
            "num_assets": 15,
            "debt_capacity": 750.0,  # Maximum debt limit
            "working_capital_impact": 50.0,
            "strategic_importance_score": 8.5
        }
    },
    "NPV with Inflation": {
        "description": """**NPV Calculator with Inflation**
        
Build an NPV calculator for lease vs buy decisions that incorporates: Pakistan's inflation rate (25-30%), 
currency devaluation impact on imported equipment, variable interest rates (3-month KIBOR fluctuations), 
tax rate changes, and depreciation schedules. Apply to a PKR 200 million imported processing equipment 
decision with 10-year useful life.""",
        "params": {
            "purchase_price": 200.0,
            "useful_life": 10,
            "residual_value": 30.0,  # 15% salvage
            "maintenance": 6.0,  # 3% annually
            "lease_payment": 36.0,  # Annual lease
            "discount_rate": 12.0,
            "tax_rate": 29.0,
            "inflation_rate": 27.5,  # Average 25-30%
            "currency_devaluation": 8.0,  # Annual PKR devaluation
            "kibor_fluctuation": 3.5,  # KIBOR volatility
            "imported_equipment": True
        }
    },
    "Cash Flow Forecasting": {
        "description": """**Cash Flow Forecasting Model**
        
Develop a 5-year monthly cash flow forecast comparing lease vs buy for PKR 300 million in capital equipment. 
Include: seasonal revenue variations (Ramadan spikes), working capital cycles, debt service coverage ratios 
(minimum 1.25x), dividend payment constraints, and credit facility utilization. Show which option optimizes 
cash availability.""",
        "params": {
            "purchase_price": 300.0,
            "useful_life": 5,
            "residual_value": 60.0,  # 20% salvage
            "maintenance": 9.0,  # 3% annually
            "lease_payment": 72.0,  # Annual lease
            "discount_rate": 12.0,
            "tax_rate": 29.0,
            "seasonal_variance": 35.0,  # Ramadan spike %
            "min_dscr": 1.25,  # Minimum debt service coverage
            "dividend_payout": 15.0,  # Annual dividend
            "credit_facility": 200.0,  # Available credit line
            "working_capital_requirement": 75.0
        }
    },
    "Growth Scenario Analysis": {
        "description": """**Growth Scenario Analysis**
        
Analyze lease vs buy under three growth scenarios for production equipment: conservative (5% annual growth), 
base case (12% growth), aggressive (25% growth). Consider: capacity utilization, scalability needs, 
obsolescence risks, and financial flexibility. For a PKR 250 million investment, recommend optimal strategy 
for each scenario with trigger points for switching.""",
        "params": {
            "purchase_price": 250.0,
            "useful_life": 7,
            "residual_value": 50.0,  # 20% salvage
            "maintenance": 7.5,  # 3% annually
            "lease_payment": 48.0,  # Annual lease
            "discount_rate": 12.0,
            "tax_rate": 29.0,
            "conservative_growth": 5.0,
            "base_growth": 12.0,
            "aggressive_growth": 25.0,
            "current_capacity_utilization": 72.0,
            "obsolescence_risk_score": 6.5
        }
    },
    "Economic Downturn": {
        "description": """**Economic Downturn Simulation**
        
Model lease vs buy decision under economic stress scenario: 30% revenue decline, 20% currency devaluation, 
interest rate spike to 25%, and tighter credit conditions. For a PKR 180 million cold storage expansion, 
evaluate: payment flexibility, asset liquidation options, covenant compliance, and strategic reversibility. 
Which option provides better downside protection?""",
        "params": {
            "purchase_price": 180.0,
            "useful_life": 10,
            "residual_value": 36.0,  # 20% salvage
            "maintenance": 5.4,  # 3% annually
            "lease_payment": 32.4,  # Annual lease
            "discount_rate": 25.0,  # Stress scenario rate
            "tax_rate": 29.0,
            "revenue_decline": 30.0,
            "currency_devaluation": 20.0,
            "interest_rate_spike": 25.0,
            "covenant_debt_to_equity_max": 1.5,
            "liquidation_value": 126.0,  # 70% of purchase price
            "payment_flexibility_score": 7.0
        }
    },
    "Technology Obsolescence": {
        "description": """**Technology Obsolescence Analysis**
        
Compare lease vs buy for technology-intensive food processing equipment (PKR 220 million) with high 
obsolescence risk. Analyze: 3-year, 5-year, and 7-year replacement cycles, residual value uncertainty, 
operating lease with upgrade options, manufacturer buyback programs, and competitive advantage from latest 
technology. Create a decision tree model.""",
        "params": {
            "purchase_price": 220.0,
            "useful_life": 5,  # Base case
            "residual_value": 22.0,  # 10% due to obsolescence
            "maintenance": 6.6,  # 3% annually
            "lease_payment": 52.8,  # Annual lease with upgrade option
            "discount_rate": 15.0,  # Higher due to tech risk
            "tax_rate": 29.0,
            "cycle_3_year_residual": 88.0,  # 40% residual
            "cycle_5_year_residual": 22.0,  # 10% residual
            "cycle_7_year_residual": 11.0,  # 5% residual
            "manufacturer_buyback": 55.0,  # 25% guaranteed buyback
            "obsolescence_probability": 65.0,  # High risk
            "competitive_advantage_value": 30.0
        }
    },
    "Tax Shield Optimization": {
        "description": """**Tax Shield Optimization**
        
Calculate optimal lease vs buy decision from tax perspective for PKR 400 million in assets. Include: 
depreciation tax shields (15% declining balance), lease payment deductibility, Alternative Corporate Tax 
(ACT) implications, minimum tax considerations (1.25% of turnover), and timing of tax benefits. Show which 
option minimizes effective tax rate.""",
        "params": {
            "purchase_price": 400.0,
            "useful_life": 10,
            "residual_value": 40.0,  # 10% salvage
            "maintenance": 12.0,  # 3% annually
            "lease_payment": 72.0,  # Annual lease
            "discount_rate": 12.0,
            "tax_rate": 29.0,
            "depreciation_rate_declining": 15.0,  # Declining balance
            "act_rate": 17.0,  # Alternative Corporate Tax
            "minimum_tax_rate": 1.25,  # % of turnover
            "annual_turnover": 5000.0,
            "minimum_tax": 62.5,  # 1.25% of 5000M
            "tax_loss_carryforward": 25.0
        }
    },
    "Balance Sheet Impact": {
        "description": """**Balance Sheet Impact Analysis**
        
Evaluate how lease vs buy affects Fauji Foods' key financial ratios for PKR 350 million equipment purchase. 
Analyze impact on: debt-to-equity ratio (current 1.2:1, covenant maximum 1.5:1), current ratio, return on 
assets, interest coverage ratio, and IFRS 16 lease liability recognition. Determine which option maintains 
optimal capital structure.""",
        "params": {
            "purchase_price": 350.0,
            "useful_life": 8,
            "residual_value": 52.5,  # 15% salvage
            "maintenance": 10.5,  # 3% annually
            "lease_payment": 63.0,  # Annual lease
            "discount_rate": 12.0,
            "tax_rate": 29.0,
            "current_debt_to_equity": 1.2,
            "covenant_max_debt_to_equity": 1.5,
            "current_ratio": 1.8,
            "current_roa": 5.6,  # Return on Assets %
            "current_interest_coverage": 4.5,
            "ifrs16_lease_liability": 315.0,  # PV of lease payments
            "current_total_assets": BASE_ASSETS,
            "current_total_equity": BASE_EQUITY
        }
    },
    "Off-Balance Sheet": {
        "description": """**Off-Balance Sheet Financing**
        
Assess viability of operating leases to keep assets off balance sheet for PKR 500 million expansion 
(10 different assets). Consider: IFRS 16 requirements, lender covenant calculations, credit rating impact, 
financial statement presentation, and investor perception. Is off-balance sheet treatment still achievable 
and beneficial?""",
        "params": {
            "purchase_price": 500.0,
            "useful_life": 7,
            "residual_value": 75.0,  # 15% salvage
            "maintenance": 15.0,  # 3% annually
            "lease_payment": 90.0,  # Annual operating lease
            "discount_rate": 12.0,
            "tax_rate": 29.0,
            "num_assets": 10,
            "ifrs16_applicable": True,
            "lease_term_vs_useful_life": 71.0,  # 5 years / 7 years = 71%
            "pv_lease_payments": 450.0,
            "credit_rating_current": "A-",
            "covenant_exclusion_possible": False,  # IFRS 16 impact
            "investor_transparency_score": 7.5
        }
    },
    "Strategic Flexibility": {
        "description": """**Strategic Flexibility Valuation**
        
Quantify the value of flexibility in lease vs buy for PKR 280 million asset portfolio. Use real options 
approach to value: option to expand (20% probability), option to abandon (15% probability), option to switch 
suppliers (30% probability), and option to upgrade technology (40% probability). Apply to decision between 
7-year lease and purchase.""",
        "params": {
            "purchase_price": 280.0,
            "useful_life": 7,
            "residual_value": 56.0,  # 20% salvage
            "maintenance": 8.4,  # 3% annually
            "lease_payment": 56.0,  # Annual lease
            "discount_rate": 15.0,  # Higher for real options
            "tax_rate": 29.0,
            "option_expand_prob": 20.0,
            "option_expand_value": 140.0,  # 50% additional investment
            "option_abandon_prob": 15.0,
            "option_abandon_value": 84.0,  # 30% recovery
            "option_switch_prob": 30.0,
            "option_switch_value": 42.0,  # Switching cost
            "option_upgrade_prob": 40.0,
            "option_upgrade_value": 112.0,  # Upgrade investment
            "volatility": 35.0  # Business volatility for options
        }
    },
    "Vendor Dependency Risk": {
        "description": """**Vendor Dependency Risk**
        
Analyze lease vs buy for critical production equipment (PKR 160 million) considering: single-supplier 
dependency, geopolitical risks (equipment from China), spare parts availability, technical support quality, 
and alternative vendor options. Evaluate whether ownership provides better operational security vs lease 
convenience.""",
        "params": {
            "purchase_price": 160.0,
            "useful_life": 8,
            "residual_value": 32.0,  # 20% salvage
            "maintenance": 4.8,  # 3% annually
            "lease_payment": 32.0,  # Annual lease
            "discount_rate": 14.0,  # Higher due to vendor risk
            "tax_rate": 29.0,
            "vendor_dependency_score": 8.5,  # High dependency (out of 10)
            "geopolitical_risk_premium": 3.5,  # Additional risk %
            "spare_parts_lead_time_days": 90,  # From China
            "technical_support_score": 6.0,  # Limited local support
            "alternative_vendors_available": 2,
            "supply_chain_disruption_prob": 25.0,  # 25% probability
            "downtime_cost_per_day": 0.5,  # PKR 0.5M per day
            "operational_security_premium": 15.0  # Value of ownership control
        }
    },
    "Market Positioning Strategy": {
        "description": """**Market Positioning Strategy**
        
Create decision framework for lease vs buy that aligns with Fauji Foods' market leadership strategy. For 
PKR 600 million in new capacity additions, evaluate: first-mover advantage timing, competitor response 
implications, market share targets (25% to 30%), capital intensity vs asset-light model, and investor 
expectations. Recommend strategic approach.""",
        "params": {
            "purchase_price": 600.0,
            "useful_life": 10,
            "residual_value": 120.0,  # 20% salvage
            "maintenance": 18.0,  # 3% annually
            "lease_payment": 96.0,  # Annual lease
            "discount_rate": 12.0,
            "tax_rate": 29.0,
            "current_market_share": 25.0,
            "target_market_share": 30.0,
            "first_mover_advantage_value": 80.0,  # Market timing premium
            "competitor_response_lag_months": 18,
            "capital_intensity_ratio": 0.65,  # Assets/Revenue
            "asset_light_target_ratio": 0.45,  # Target for asset-light model
            "investor_roe_expectation": 18.0,  # Expected ROE %
            "brand_premium_value": 45.0,  # Market leadership premium
            "time_to_market_months": 12  # Implementation timeline
        }
    },
    "Food Safety Compliance": {
        "description": """**Food Safety Equipment Compliance**
        
Evaluate lease vs buy for HACCP-compliant food safety equipment and laboratory testing systems (PKR 95 
million). Include: regulatory update frequency, certification costs, technology evolution pace, audit 
readiness, and quality assurance ROI. Consider that leasing may include compliance updates while ownership 
requires separate upgrade investments.""",
        "params": {
            "purchase_price": 95.0,
            "useful_life": 6,
            "residual_value": 14.25,  # 15% salvage (tech-intensive)
            "maintenance": 2.85,  # 3% annually
            "lease_payment": 21.0,  # Annual lease with updates included
            "discount_rate": 12.0,
            "tax_rate": 29.0,
            "regulatory_update_frequency_years": 2,
            "certification_cost_per_update": 3.5,  # PKR 3.5M per update
            "haccp_compliance_cost_annual": 4.0,
            "audit_readiness_score": 9.0,  # High importance (out of 10)
            "quality_assurance_roi": 25.0,  # 25% ROI from QA improvements
            "technology_evolution_rate": 15.0,  # 15% annual tech improvement
            "lease_includes_updates": True,
            "compliance_risk_penalty": 50.0,  # Cost of non-compliance
            "brand_reputation_value": 30.0  # Reputation protection value
        }
    },
    "Energy-Intensive Assets": {
        "description": """**Energy-Intensive Asset Decision**
        
Analyze lease vs buy for energy-intensive baking ovens and dryers (PKR 270 million) during Pakistan's 
energy crisis. Factor in: electricity tariff volatility, gas supply interruptions, solar/alternative energy 
integration, energy efficiency improvements (3% annually), and government industrial package benefits. 
Calculate total energy-adjusted cost of ownership.""",
        "params": {
            "purchase_price": 270.0,
            "useful_life": 12,
            "residual_value": 54.0,  # 20% salvage
            "maintenance": 8.1,  # 3% annually
            "lease_payment": 45.0,  # Annual lease
            "discount_rate": 12.0,
            "tax_rate": 29.0,
            "annual_electricity_cost": 48.0,  # PKR 48M annually
            "annual_gas_cost": 36.0,  # PKR 36M annually
            "electricity_tariff_increase": 15.0,  # 15% annual increase
            "gas_supply_interruption_days": 45,  # Days per year
            "solar_integration_cost": 35.0,  # PKR 35M for solar
            "solar_energy_offset": 40.0,  # 40% energy from solar
            "energy_efficiency_improvement": 3.0,  # 3% annual improvement
            "govt_industrial_package_subsidy": 25.0,  # PKR 25M subsidy
            "production_downtime_cost": 1.2,  # PKR 1.2M per day
            "alternative_fuel_option_value": 18.0  # Value of fuel flexibility
        }
    },
    "Cross-Border Islamic Leasing": {
        "description": """**Cross-Border Leasing Opportunity**
        
Evaluate an Islamic Ijarah (leasing) structure from Middle Eastern lessor for PKR 320 million food 
processing equipment vs conventional purchase financing from local banks. Compare: Shariah compliance, 
forex exposure (USD-denominated lease vs PKR loan), political risk insurance, profit rates (8% Ijarah vs 
21% bank loan), and reputational considerations for Fauji Foods' brand. Provide comprehensive recommendation.""",
        "params": {
            "purchase_price": 320.0,
            "useful_life": 8,
            "residual_value": 64.0,  # 20% salvage
            "maintenance": 9.6,  # 3% annually
            "lease_payment": 38.4,  # Annual Ijarah (8% profit rate)
            "discount_rate": 12.0,
            "tax_rate": 29.0,
            "ijarah_profit_rate": 8.0,  # Islamic lease rate
            "conventional_loan_rate": 21.0,  # Local bank rate
            "usd_denomination": True,
            "usd_pkr_rate": 278.0,  # Current exchange rate
            "forex_volatility": 12.0,  # 12% annual PKR volatility
            "political_risk_insurance_cost": 2.5,  # PKR 2.5M annually
            "shariah_compliance_value": 20.0,  # Brand/reputation value
            "middle_east_lessor_rating": "AA",
            "local_bank_rating": "A+",
            "hedging_cost_percentage": 3.0,  # 3% of exposure
            "reputational_premium": 15.0,  # Islamic finance brand boost
            "cross_border_transaction_cost": 4.0  # One-time cost
        }
    }
}

# ==============================
# TABS
# ==============================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Decision Analysis",
    "📜 Historical Financials",
    "🏦 Financial Impact",
    "🎯 Predefined Scenarios"
])

# ==============================
# TAB 1: DECISION ANALYSIS + GRAPH
# ==============================
with tab1:
    c1, c2, c3 = st.columns(3)
    c1.metric("NPV (Buy)", fmt(npv_buy))
    c2.metric("NPV (Lease)", fmt(npv_lease))
    c3.metric("Net Advantage (NAL)", fmt(nal))

    st.success("Leasing is preferable" if nal > 0 else "Buying is preferable")

    st.subheader("📈 Cash Flow Comparison")

    years = list(range(0, useful_life + 1))
    cf_chart = pd.DataFrame({
        "Year": years,
        "Buy": buy_cash_flows,
        "Lease": lease_cash_flows
    }).set_index("Year")

    st.line_chart(cf_chart)

# ==============================
# TAB 2: HISTORICAL DATA
# ==============================
with tab2:
    historic_df = pd.DataFrame({
        "Metric": ["Total Assets", "Total Liabilities", "Total Debt", "Equity", "EBIT", "Net Profit"],
        "Value": [BASE_ASSETS, BASE_LIABILITIES, BASE_DEBT, BASE_EQUITY, BASE_EBIT, BASE_NET_PROFIT]
    })

    st.dataframe(
        historic_df.style.format({"Value": "₨{:,.2f}"}),
        width='stretch'
    )

# ==============================
# TAB 3: FINANCIAL IMPACT + GRAPH
# ==============================
with tab3:
    impact_df = pd.DataFrame({
        "Metric": ["Total Assets", "Total Liabilities", "Equity", "EBIT", "Net Profit"],
        "Baseline": [BASE_ASSETS, BASE_LIABILITIES, BASE_EQUITY, BASE_EBIT, BASE_NET_PROFIT],
        "After BUY": [
            BASE_ASSETS + purchase_price,
            BASE_LIABILITIES + (purchase_price if purchase_mode == "Credit" else 0),
            BASE_EQUITY,
            BASE_EBIT - maintenance + depreciation,
            BASE_NET_PROFIT + dep_tax_shield - maintenance * (1 - tax_rate)
        ],
        "After LEASE": [
            BASE_ASSETS + purchase_price,
            BASE_LIABILITIES + purchase_price,
            BASE_EQUITY,
            BASE_EBIT - lease_payment,
            BASE_NET_PROFIT - lease_payment * (1 - tax_rate)
        ]
    })

    st.dataframe(
        impact_df.style.format({
            "Baseline": "₨{:,.2f}",
            "After BUY": "₨{:,.2f}",
            "After LEASE": "₨{:,.2f}"
        }),
        width='stretch'
    )

    st.subheader("📊 Financial Impact Comparison")
    st.bar_chart(impact_df.set_index("Metric"))

# ==============================
# TAB 4: PREDEFINED SCENARIOS
# ==============================
with tab4:
    st.header("🎯 Predefined Lease vs Buy Scenarios")
    st.markdown("""
    Select from comprehensive, real-world scenarios tailored for Fauji Foods Limited. 
    Each scenario includes detailed parameters and industry-specific considerations.
    """)
    
    # Scenario Categories
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📦 Equipment & Machinery")
        st.markdown("• Production Line Equipment\n• Packaging Machinery\n• Cold Storage Equipment")
        
        st.subheader("🚚 Fleet & Transportation")
        st.markdown("• Distribution Truck Fleet\n• Refrigerated Transport")
        
        st.subheader("🏭 Real Estate & Facilities")
        st.markdown("• Warehouse Facility\n• Retail Outlet Expansion\n• Factory Land Acquisition")
        
        st.subheader("💻 Technology & Systems")
        st.markdown("• ERP System\n• Solar Power System")
    
    with col_right:
        st.subheader("📊 Financial Analysis Tools")
        st.markdown("• Multi-Asset Portfolio\n• NPV with Inflation\n• Cash Flow Forecasting")
        
        st.subheader("📈 Comparative Scenarios")
        st.markdown("• Growth Scenario Analysis\n• Economic Downturn\n• Technology Obsolescence")
        
        st.subheader("💰 Tax & Accounting Impact")
        st.markdown("• Tax Shield Optimization\n• Balance Sheet Impact\n• Off-Balance Sheet")
        
        st.subheader("🎲 Strategic & Risk Assessment")
        st.markdown("• Strategic Flexibility")
        
        st.subheader("🌐 Specialized Sector Decisions")
        st.markdown("• Vendor Dependency Risk\n• Market Positioning Strategy\n• Food Safety Compliance\n• Energy-Intensive Assets\n• Cross-Border Islamic Leasing")
    
    # Scenario Selection
    st.markdown("---")
    scenario_choice = st.selectbox(
        "Select a Scenario to Analyze:",
        ["-- Choose a Scenario --"] + list(SCENARIOS.keys())
    )
    
    if scenario_choice != "-- Choose a Scenario --":
        scenario = SCENARIOS[scenario_choice]
        
        # Display scenario description
        st.info(scenario["description"])
        
        # Get parameters
        params = scenario["params"]
        
        # Calculate scenario-specific analysis
        st.markdown("---")
        st.subheader("📊 Financial Analysis")
        
        # Extract parameters
        pp = params["purchase_price"]
        ul = params["useful_life"]
        rv = params["residual_value"]
        maint = params["maintenance"]
        lp = params["lease_payment"]
        dr = params["discount_rate"] / 100
        tr = params["tax_rate"] / 100
        
        # Buy option cash flows
        # Check for declining balance depreciation
        if params.get("depreciation_rate_declining"):
            dep_rate = params["depreciation_rate_declining"] / 100
            dep_scenario = None  # Variable depreciation
        else:
            dep_scenario = (pp - rv) / ul
            dep_tax_scenario = dep_scenario * tr
        
        # Check if subsidy exists
        subsidy = params.get("aedb_subsidy", 0) + params.get("government_subsidy", 0)
        net_purchase_price = pp - subsidy
        
        # Adjust for down payment
        if "down_payment" in params:
            initial_outlay = params["down_payment"]
            financed_amount = pp - initial_outlay
        else:
            initial_outlay = net_purchase_price
            financed_amount = 0
        
        buy_cf_scenario = [-initial_outlay]
        book_value = pp
        
        for year in range(ul):
            # Handle declining balance depreciation
            if params.get("depreciation_rate_declining"):
                dep_year = book_value * dep_rate
                dep_tax_year = dep_year * tr
                book_value -= dep_year
            else:
                dep_tax_year = dep_tax_scenario
            
            # Base cash flow
            cf = dep_tax_year - maint * (1 - tr)
            
            # Add electricity savings for solar
            if "electricity_savings" in params:
                elec_savings = params["electricity_savings"] * ((1 + params["tariff_increase"]/100) ** year)
                cf += elec_savings
            
            # Adjust for inflation
            if "inflation_rate" in params:
                inflation_adj = 1 / ((1 + params["inflation_rate"]/100) ** year)
                cf *= inflation_adj
            
            # Add growth scenario benefits
            if "base_growth" in params:
                growth_benefit = pp * (params["base_growth"]/100) * (year + 1) * 0.1
                cf += growth_benefit
            
            # Add strategic flexibility value (real options)
            if "option_expand_prob" in params and year == 3:  # Mid-life option
                option_value = (
                    params["option_expand_prob"]/100 * params["option_expand_value"] * 0.2 +
                    params["option_upgrade_prob"]/100 * params["option_upgrade_value"] * 0.15
                )
                cf += option_value
            
            buy_cf_scenario.append(cf)
        
        # Terminal value considerations
        terminal_value = rv
        
        # Adjust for economic downturn scenario
        if "liquidation_value" in params:
            terminal_value = params["liquidation_value"] * 0.5 + rv * 0.5
        
        # Adjust for technology obsolescence
        if "obsolescence_probability" in params:
            obs_prob = params["obsolescence_probability"] / 100
            terminal_value = rv * (1 - obs_prob) + params.get("manufacturer_buyback", rv * 0.5) * obs_prob
        
        buy_cf_scenario[-1] += terminal_value
        npv_scenario_buy = calculate_npv(dr, buy_cf_scenario)
        
        # Lease option cash flows
        lease_cf_scenario = [0]
        for year in range(ul):
            # Check for lease escalation
            if "lease_escalation" in params and year > 0 and year % 3 == 0:
                escalation_factor = (1 + params["lease_escalation"]/100) ** (year // 3)
                adjusted_lp = lp * escalation_factor
            else:
                adjusted_lp = lp
            
            cf = -adjusted_lp * (1 - tr)
            
            # Add electricity savings for solar lease option
            if "electricity_savings" in params:
                elec_savings = params["electricity_savings"] * ((1 + params["tariff_increase"]/100) ** year)
                cf += elec_savings
            
            # Adjust for inflation
            if "inflation_rate" in params:
                inflation_adj = 1 / ((1 + params["inflation_rate"]/100) ** year)
                cf *= inflation_adj
            
            # Add growth scenario benefits (leasing offers flexibility)
            if "base_growth" in params:
                growth_benefit = pp * (params["base_growth"]/100) * (year + 1) * 0.12  # Higher for lease flexibility
                cf += growth_benefit
            
            # Flexibility premium for leasing under uncertainty
            if "revenue_decline" in params:  # Economic downturn scenario
                flexibility_premium = adjusted_lp * 0.15  # 15% flexibility value
                cf += flexibility_premium
            
            # Strategic flexibility value for leasing
            if "option_expand_prob" in params:
                lease_flexibility = (
                    params["option_expand_prob"]/100 * 0.25 * adjusted_lp +
                    params["option_abandon_prob"]/100 * 0.30 * adjusted_lp +
                    params["option_switch_prob"]/100 * 0.20 * adjusted_lp
                )
                cf += lease_flexibility
            
            lease_cf_scenario.append(cf)
        
        npv_scenario_lease = calculate_npv(dr, lease_cf_scenario)
        nal_scenario = npv_scenario_buy - npv_scenario_lease
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Purchase Price", fmt(pp))
        col2.metric("NPV (Buy)", fmt(npv_scenario_buy), 
                   delta=f"{npv_scenario_buy/pp*100:.1f}% ROI")
        col3.metric("NPV (Lease)", fmt(npv_scenario_lease),
                   delta=f"{npv_scenario_lease/pp*100:.1f}% ROI")
        col4.metric("Net Advantage (NAL)", fmt(nal_scenario))
        
        # Recommendation
        if nal_scenario > 0:
            st.success(f"✅ **Recommendation: LEASE** - Leasing provides a net advantage of {fmt(nal_scenario)} in NPV terms.")
        else:
            st.success(f"✅ **Recommendation: BUY** - Purchasing provides a net advantage of {fmt(abs(nal_scenario))} in NPV terms.")
        
        # Additional scenario-specific metrics
        st.markdown("---")
        st.subheader("📈 Scenario-Specific Metrics")
        
        metrics_col1, metrics_col2 = st.columns(2)
        
        with metrics_col1:
            st.markdown("**Key Parameters:**")
            for key, value in params.items():
                if key not in ["purchase_price", "useful_life", "residual_value", "maintenance", 
                              "lease_payment", "discount_rate", "tax_rate"]:
                    if isinstance(value, (int, float)):
                        if value >= 1:
                            st.write(f"- **{key.replace('_', ' ').title()}:** {fmt(value)}")
                        else:
                            st.write(f"- **{key.replace('_', ' ').title()}:** {value}%")
                    else:
                        st.write(f"- **{key.replace('_', ' ').title()}:** {value}")
        
        with metrics_col2:
            st.markdown("**Financial Ratios:**")
            # Payback period (simplified)
            if npv_scenario_buy > 0:
                annual_benefit = (npv_scenario_buy + net_purchase_price) / ul
                payback_buy = net_purchase_price / annual_benefit if annual_benefit > 0 else 0
                st.write(f"- **Payback Period (Buy):** {payback_buy:.2f} years")
            
            if npv_scenario_lease > 0:
                annual_lease_cost = lp
                st.write(f"- **Annual Lease Cost:** {fmt(annual_lease_cost)}")
            
            # Break-even analysis
            breakeven_rate = (lp / pp) * 100
            st.write(f"- **Break-even Rate:** {breakeven_rate:.2f}%")
            
            # Total cost of ownership
            tco_buy = net_purchase_price + (maint * ul) - terminal_value
            tco_lease = lp * ul
            st.write(f"- **TCO (Buy):** {fmt(tco_buy)}")
            st.write(f"- **TCO (Lease):** {fmt(tco_lease)}")
            
            # Effective cost per year
            effective_cost_buy = tco_buy / ul
            effective_cost_lease = tco_lease / ul
            st.write(f"- **Effective Annual Cost (Buy):** {fmt(effective_cost_buy)}")
            st.write(f"- **Effective Annual Cost (Lease):** {fmt(effective_cost_lease)}")
        
        # Advanced scenario-specific analysis
        st.markdown("---")
        
        # Multi-Asset Portfolio Analysis
        if "num_assets" in params:
            st.subheader("🎯 Portfolio Optimization Analysis")
            col_p1, col_p2, col_p3 = st.columns(3)
            with col_p1:
                st.metric("Number of Assets", params["num_assets"])
                st.metric("WACC", f"{dr*100:.1f}%")
            with col_p2:
                st.metric("Debt Capacity", fmt(params["debt_capacity"]))
                st.metric("Working Capital Impact", fmt(params["working_capital_impact"]))
            with col_p3:
                st.metric("Strategic Importance", f"{params['strategic_importance_score']}/10")
                optimal_mix = "60% Buy / 40% Lease" if nal_scenario > 0 else "40% Buy / 60% Lease"
                st.metric("Optimal Mix", optimal_mix)
        
        # Inflation & Currency Impact
        if "inflation_rate" in params:
            st.subheader("📉 Inflation & Currency Analysis")
            col_i1, col_i2, col_i3 = st.columns(3)
            with col_i1:
                st.metric("Inflation Rate", f"{params['inflation_rate']:.1f}%")
                real_npv_buy = npv_scenario_buy / ((1 + params['inflation_rate']/100) ** ul)
                st.metric("Real NPV (Buy)", fmt(real_npv_buy))
            with col_i2:
                st.metric("Currency Devaluation", f"{params['currency_devaluation']:.1f}%")
                real_npv_lease = npv_scenario_lease / ((1 + params['inflation_rate']/100) ** ul)
                st.metric("Real NPV (Lease)", fmt(real_npv_lease))
            with col_i3:
                st.metric("KIBOR Volatility", f"{params['kibor_fluctuation']:.1f}%")
                inflation_adjusted_nal = real_npv_buy - real_npv_lease
                st.metric("Real NAL", fmt(inflation_adjusted_nal))
        
        # Growth Scenario Analysis
        if "conservative_growth" in params:
            st.subheader("📈 Growth Scenario Impact")
            growth_df = pd.DataFrame({
                "Scenario": ["Conservative", "Base Case", "Aggressive"],
                "Growth Rate": [f"{params['conservative_growth']}%", f"{params['base_growth']}%", f"{params['aggressive_growth']}%"],
                "NPV (Buy)": [
                    npv_scenario_buy * 0.85,
                    npv_scenario_buy,
                    npv_scenario_buy * 1.35
                ],
                "NPV (Lease)": [
                    npv_scenario_lease * 0.90,
                    npv_scenario_lease,
                    npv_scenario_lease * 1.25
                ],
                "Recommendation": [
                    "Lease" if npv_scenario_lease * 0.90 > npv_scenario_buy * 0.85 else "Buy",
                    "Lease" if nal_scenario > 0 else "Buy",
                    "Lease" if npv_scenario_lease * 1.25 > npv_scenario_buy * 1.35 else "Buy"
                ]
            })
            st.dataframe(
                growth_df.style.format({
                    "NPV (Buy)": "₨{:,.2f}M",
                    "NPV (Lease)": "₨{:,.2f}M"
                }),
                width='stretch'
            )
        
        # Economic Downturn Impact
        if "revenue_decline" in params:
            st.subheader("⚠️ Economic Stress Test")
            col_s1, col_s2, col_s3, col_s4 = st.columns(4)
            with col_s1:
                st.metric("Revenue Decline", f"-{params['revenue_decline']:.0f}%", delta_color="inverse")
            with col_s2:
                st.metric("Interest Rate Spike", f"{params['interest_rate_spike']:.0f}%", delta_color="inverse")
            with col_s3:
                st.metric("Liquidation Value", fmt(params['liquidation_value']))
            with col_s4:
                flexibility_score = params['payment_flexibility_score']
                st.metric("Flexibility Score", f"{flexibility_score}/10")
            
            st.info(f"Under stress conditions, **{'LEASING' if flexibility_score > 7 else 'BUYING'}** provides better downside protection.")
        
        # Technology Obsolescence
        if "obsolescence_probability" in params:
            st.subheader("🔄 Technology Lifecycle Analysis")
            col_t1, col_t2, col_t3 = st.columns(3)
            with col_t1:
                st.metric("Obsolescence Risk", f"{params['obsolescence_probability']:.0f}%")
                st.metric("3-Year Residual", fmt(params['cycle_3_year_residual']))
            with col_t2:
                st.metric("Manufacturer Buyback", fmt(params['manufacturer_buyback']))
                st.metric("5-Year Residual", fmt(params['cycle_5_year_residual']))
            with col_t3:
                st.metric("Competitive Advantage", fmt(params['competitive_advantage_value']))
                st.metric("7-Year Residual", fmt(params['cycle_7_year_residual']))
            
            st.warning("High obsolescence risk favors **LEASING** for technology refresh flexibility.")
        
        # Tax Optimization
        if "depreciation_rate_declining" in params:
            st.subheader("💰 Tax Shield Analysis")
            col_tx1, col_tx2, col_tx3 = st.columns(3)
            
            # Calculate declining balance depreciation schedule
            db_schedule = []
            bv = pp
            for y in range(min(5, ul)):
                dep = bv * (params['depreciation_rate_declining']/100)
                tax_shield = dep * tr
                db_schedule.append({"Year": y+1, "Depreciation": dep, "Tax Shield": tax_shield})
                bv -= dep
            
            with col_tx1:
                st.metric("Depreciation Method", "Declining Balance")
                st.metric("Rate", f"{params['depreciation_rate_declining']:.0f}%")
            with col_tx2:
                first_year_shield = db_schedule[0]["Tax Shield"] if db_schedule else 0
                st.metric("First Year Tax Shield", fmt(first_year_shield))
                total_tax_shield = sum(item["Tax Shield"] for item in db_schedule)
                st.metric(f"Total Tax Shield ({min(5, ul)}Y)", fmt(total_tax_shield))
            with col_tx3:
                st.metric("Minimum Tax", fmt(params.get('minimum_tax', 0)))
                st.metric("ACT Rate", f"{params.get('act_rate', 0):.0f}%")
            
            if db_schedule:
                st.markdown("**Depreciation Schedule (First 5 Years):**")
                st.dataframe(
                    pd.DataFrame(db_schedule).style.format({
                        "Depreciation": "₨{:,.2f}M",
                        "Tax Shield": "₨{:,.2f}M"
                    }),
                    width='stretch'
                )
        
        # Balance Sheet Impact
        if "current_debt_to_equity" in params:
            st.subheader("📊 Balance Sheet Impact")
            col_bs1, col_bs2, col_bs3 = st.columns(3)
            
            # Calculate new ratios
            new_debt_buy = BASE_DEBT + (pp if "Credit" in str(params) else 0)
            new_debt_lease = BASE_DEBT + params.get('ifrs16_lease_liability', pp * 0.9)
            
            new_de_buy = new_debt_buy / BASE_EQUITY
            new_de_lease = new_debt_lease / BASE_EQUITY
            
            new_assets_buy = BASE_ASSETS + pp
            new_assets_lease = BASE_ASSETS + params.get('ifrs16_lease_liability', pp * 0.9)
            
            new_roa_buy = (BASE_NET_PROFIT * 1.1) / new_assets_buy * 100
            new_roa_lease = (BASE_NET_PROFIT * 1.05) / new_assets_lease * 100
            
            with col_bs1:
                st.metric("Current D/E Ratio", f"{params['current_debt_to_equity']:.2f}")
                st.metric("D/E after Buy", f"{new_de_buy:.2f}", 
                         delta=f"{((new_de_buy/params['current_debt_to_equity']-1)*100):.1f}%",
                         delta_color="inverse")
                st.metric("D/E after Lease", f"{new_de_lease:.2f}",
                         delta=f"{((new_de_lease/params['current_debt_to_equity']-1)*100):.1f}%",
                         delta_color="inverse")
            with col_bs2:
                st.metric("Covenant Max D/E", f"{params['covenant_max_debt_to_equity']:.2f}")
                covenant_headroom_buy = params['covenant_max_debt_to_equity'] - new_de_buy
                covenant_headroom_lease = params['covenant_max_debt_to_equity'] - new_de_lease
                st.metric("Headroom (Buy)", f"{covenant_headroom_buy:.2f}")
                st.metric("Headroom (Lease)", f"{covenant_headroom_lease:.2f}")
            with col_bs3:
                st.metric("Current ROA", f"{params['current_roa']:.1f}%")
                st.metric("ROA after Buy", f"{new_roa_buy:.1f}%",
                         delta=f"{(new_roa_buy - params['current_roa']):.1f}%")
                st.metric("ROA after Lease", f"{new_roa_lease:.1f}%",
                         delta=f"{(new_roa_lease - params['current_roa']):.1f}%")
            
            # Covenant compliance check
            if new_de_buy > params['covenant_max_debt_to_equity']:
                st.error("⚠️ **Buy option violates debt covenant!** Consider leasing or equity financing.")
            elif new_de_lease > params['covenant_max_debt_to_equity']:
                st.error("⚠️ **Lease option violates debt covenant!** Consider equity financing.")
            else:
                st.success("✅ Both options maintain covenant compliance.")
        
        # IFRS 16 & Off-Balance Sheet
        if "ifrs16_applicable" in params:
            st.subheader("📋 IFRS 16 & Off-Balance Sheet Analysis")
            col_ifrs1, col_ifrs2 = st.columns(2)
            
            with col_ifrs1:
                st.markdown("**IFRS 16 Requirements:**")
                st.write(f"- **Lease Liability:** {fmt(params.get('pv_lease_payments', 0))}")
                st.write(f"- **Right-of-Use Asset:** {fmt(params.get('pv_lease_payments', 0))}")
                st.write(f"- **Lease Term vs Useful Life:** {params.get('lease_term_vs_useful_life', 0):.0f}%")
                st.write(f"- **Number of Assets:** {params.get('num_assets', 1)}")
                
            with col_ifrs2:
                st.markdown("**Impact Assessment:**")
                st.write(f"- **Current Credit Rating:** {params.get('credit_rating_current', 'N/A')}")
                st.write(f"- **Covenant Exclusion:** {'❌ No' if not params.get('covenant_exclusion_possible') else '✅ Yes'}")
                st.write(f"- **Investor Transparency:** {params.get('investor_transparency_score', 0)}/10")
                
            if params['ifrs16_applicable']:
                st.warning("⚠️ **IFRS 16 applies**: Operating leases must be capitalized. True off-balance sheet treatment is no longer achievable.")
            else:
                st.info("✅ Off-balance sheet treatment may be possible under specific conditions.")
        
        # Real Options & Strategic Flexibility
        if "option_expand_prob" in params:
            st.subheader("🎲 Real Options Valuation")
            
            # Calculate option values
            expand_value = params['option_expand_prob']/100 * params['option_expand_value']
            abandon_value = params['option_abandon_prob']/100 * params['option_abandon_value']
            switch_value = params['option_switch_prob']/100 * params['option_switch_value']
            upgrade_value = params['option_upgrade_prob']/100 * params['option_upgrade_value']
            total_option_value = expand_value + abandon_value + switch_value + upgrade_value
            
            options_df = pd.DataFrame({
                "Option Type": ["Expand", "Abandon", "Switch Supplier", "Upgrade Technology", "**Total**"],
                "Probability": [
                    f"{params['option_expand_prob']:.0f}%",
                    f"{params['option_abandon_prob']:.0f}%",
                    f"{params['option_switch_prob']:.0f}%",
                    f"{params['option_upgrade_prob']:.0f}%",
                    "—"
                ],
                "Potential Value": [
                    params['option_expand_value'],
                    params['option_abandon_value'],
                    params['option_switch_value'],
                    params['option_upgrade_value'],
                    0
                ],
                "Expected Value": [
                    expand_value,
                    abandon_value,
                    switch_value,
                    upgrade_value,
                    total_option_value
                ]
            })
            
            st.dataframe(
                options_df.style.format({
                    "Potential Value": "₨{:,.2f}M",
                    "Expected Value": "₨{:,.2f}M"
                }),
                width='stretch'
            )
            
            col_opt1, col_opt2 = st.columns(2)
            with col_opt1:
                st.metric("Total Option Value", fmt(total_option_value))
                st.metric("Business Volatility", f"{params['volatility']:.0f}%")
            with col_opt2:
                flexibility_premium = total_option_value / pp * 100
                st.metric("Flexibility Premium", f"{flexibility_premium:.1f}%")
                st.info(f"**Leasing** captures {flexibility_premium * 0.7:.1f}% of option value through flexibility.")
        
        # Cash Flow & DSCR Analysis
        if "min_dscr" in params:
            st.subheader("💵 Cash Flow & Debt Service Analysis")
            col_cf1, col_cf2, col_cf3 = st.columns(3)
            
            with col_cf1:
                st.metric("Min DSCR Requirement", f"{params['min_dscr']:.2f}x")
                st.metric("Seasonal Variance", f"±{params.get('seasonal_variance', 0):.0f}%")
            with col_cf2:
                st.metric("Working Capital Required", fmt(params.get('working_capital_requirement', 0)))
                st.metric("Credit Facility Available", fmt(params.get('credit_facility', 0)))
            with col_cf3:
                st.metric("Annual Dividend", fmt(params.get('dividend_payout', 0)))
                # Simplified DSCR calculation
                annual_cf = (npv_scenario_buy + net_purchase_price) / ul
                debt_service = lp
                dscr = annual_cf / debt_service if debt_service > 0 else 0
                st.metric("Projected DSCR", f"{dscr:.2f}x",
                         delta="✅ Compliant" if dscr >= params['min_dscr'] else "⚠️ Below Min")
        
        # Vendor Dependency & Supply Chain Risk
        if "vendor_dependency_score" in params:
            st.subheader("⚠️ Vendor Dependency & Supply Chain Risk")
            col_v1, col_v2, col_v3, col_v4 = st.columns(4)
            
            with col_v1:
                dependency_score = params['vendor_dependency_score']
                st.metric("Vendor Dependency", f"{dependency_score}/10", 
                         delta="High Risk" if dependency_score > 7 else "Moderate",
                         delta_color="inverse" if dependency_score > 7 else "normal")
                st.metric("Alternative Vendors", params['alternative_vendors_available'])
            
            with col_v2:
                st.metric("Geopolitical Risk Premium", f"+{params['geopolitical_risk_premium']:.1f}%")
                st.metric("Spare Parts Lead Time", f"{params['spare_parts_lead_time_days']} days",
                         delta="Long" if params['spare_parts_lead_time_days'] > 60 else "Acceptable",
                         delta_color="inverse" if params['spare_parts_lead_time_days'] > 60 else "normal")
            
            with col_v3:
                st.metric("Technical Support Score", f"{params['technical_support_score']}/10")
                st.metric("Supply Disruption Risk", f"{params['supply_chain_disruption_prob']:.0f}%",
                         delta_color="inverse")
            
            with col_v4:
                downtime_risk = params['downtime_cost_per_day'] * params['spare_parts_lead_time_days']
                st.metric("Downtime Cost Risk", fmt(downtime_risk))
                st.metric("Ownership Security Premium", fmt(params['operational_security_premium']))
            
            # Risk assessment
            if dependency_score > 7 and params['supply_chain_disruption_prob'] > 20:
                st.error("🚨 **High vendor dependency risk!** Ownership provides better operational security and spare parts control.")
            elif params['technical_support_score'] < 6:
                st.warning("⚠️ **Limited local support.** Consider lease with full-service maintenance or ownership with technical training.")
            else:
                st.info("✅ Vendor risk is manageable. Both lease and buy are viable options.")
            
            # Supply chain resilience analysis
            st.markdown("**Supply Chain Resilience Score:**")
            resilience_factors = {
                "Vendor Diversification": (10 - dependency_score) * 10,
                "Technical Support Quality": params['technical_support_score'] * 10,
                "Parts Availability": max(0, 100 - params['spare_parts_lead_time_days']/3),
                "Geopolitical Stability": max(0, 100 - params['geopolitical_risk_premium'] * 10)
            }
            resilience_df = pd.DataFrame({
                "Factor": list(resilience_factors.keys()),
                "Score (%)": list(resilience_factors.values())
            })
            st.bar_chart(resilience_df.set_index("Factor"))
        
        # Market Positioning & Strategic Impact
        if "current_market_share" in params:
            st.subheader("📊 Market Positioning & Strategic Impact")
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            
            with col_m1:
                st.metric("Current Market Share", f"{params['current_market_share']:.0f}%")
                st.metric("Target Market Share", f"{params['target_market_share']:.0f}%",
                         delta=f"+{params['target_market_share'] - params['current_market_share']:.0f}%")
            
            with col_m2:
                st.metric("First-Mover Advantage", fmt(params['first_mover_advantage_value']))
                st.metric("Competitor Response Lag", f"{params['competitor_response_lag_months']} months")
            
            with col_m3:
                st.metric("Capital Intensity", f"{params['capital_intensity_ratio']:.1%}")
                st.metric("Asset-Light Target", f"{params['asset_light_target_ratio']:.1%}",
                         delta=f"{(params['asset_light_target_ratio'] - params['capital_intensity_ratio'])*100:.0f}pp")
            
            with col_m4:
                st.metric("Investor ROE Expectation", f"{params['investor_roe_expectation']:.0f}%")
                st.metric("Brand Premium Value", fmt(params['brand_premium_value']))
            
            # Strategic recommendation
            asset_light_gap = params['capital_intensity_ratio'] - params['asset_light_target_ratio']
            time_to_market = params['time_to_market_months']
            
            if asset_light_gap > 0.15 and time_to_market < 15:
                st.success(f"✅ **Strategic Recommendation: LEASE** - Supports asset-light strategy while capturing first-mover advantage in {time_to_market} months.")
            elif params['first_mover_advantage_value'] > pp * 0.15:
                st.info(f"💡 **Speed-to-Market Priority:** First-mover advantage (PKR {params['first_mover_advantage_value']:.0f}M) justifies lease for faster deployment.")
            else:
                st.info("📈 **Balanced Approach:** Consider hybrid model - lease initial capacity, buy core assets for long-term efficiency.")
            
            # ROE impact analysis
            st.markdown("**Return on Equity Impact:**")
            equity_for_buy = pp * 0.4  # Assume 40% equity financing
            equity_for_lease = pp * 0.1  # Minimal equity for lease
            
            roe_buy = (npv_scenario_buy / ul) / equity_for_buy * 100
            roe_lease = (npv_scenario_lease / ul) / equity_for_lease * 100
            
            roe_comparison = pd.DataFrame({
                "Option": ["Buy", "Lease", "Target"],
                "ROE (%)": [roe_buy, roe_lease, params['investor_roe_expectation']],
                "Equity Required": [equity_for_buy, equity_for_lease, 0]
            })
            
            col_roe1, col_roe2 = st.columns(2)
            with col_roe1:
                st.dataframe(
                    roe_comparison.style.format({
                        "ROE (%)": "{:.1f}%",
                        "Equity Required": "₨{:,.0f}M"
                    }),
                    width='stretch'
                )
            with col_roe2:
                st.bar_chart(roe_comparison.set_index("Option")["ROE (%)"])
        
        # Food Safety & Regulatory Compliance
        if "regulatory_update_frequency_years" in params:
            st.subheader("🔬 Food Safety & Regulatory Compliance")
            col_f1, col_f2, col_f3 = st.columns(3)
            
            with col_f1:
                st.metric("Regulatory Update Frequency", f"Every {params['regulatory_update_frequency_years']} years")
                num_updates = ul // params['regulatory_update_frequency_years']
                st.metric("Expected Updates (Lifetime)", f"{num_updates} times")
                update_cost_total = num_updates * params['certification_cost_per_update']
                st.metric("Total Update Costs", fmt(update_cost_total))
            
            with col_f2:
                st.metric("Annual HACCP Compliance", fmt(params['haccp_compliance_cost_annual']))
                st.metric("Audit Readiness Score", f"{params['audit_readiness_score']}/10")
                st.metric("Technology Evolution Rate", f"{params['technology_evolution_rate']:.0f}%/year")
            
            with col_f3:
                st.metric("Quality Assurance ROI", f"{params['quality_assurance_roi']:.0f}%")
                qa_benefit = pp * (params['quality_assurance_roi']/100)
                st.metric("QA Value Creation", fmt(qa_benefit))
                st.metric("Brand Reputation Value", fmt(params['brand_reputation_value']))
            
            # Lease vs Buy compliance advantage
            if params.get('lease_includes_updates', False):
                compliance_advantage = update_cost_total
                st.success(f"✅ **Leasing Advantage:** Updates included in lease saves PKR {compliance_advantage:.0f}M in upgrade costs + ensures continuous compliance.")
            else:
                st.info("💡 **Ownership Consideration:** Budget PKR {:.0f}M for regulatory updates over {:.0f} years.".format(
                    update_cost_total, ul))
            
            # Compliance risk assessment
            compliance_risk = params.get('compliance_risk_penalty', 0)
            if compliance_risk > pp * 0.3:
                st.error(f"🚨 **High compliance risk:** Non-compliance penalty (PKR {compliance_risk:.0f}M) exceeds 30% of asset value. Choose option with guaranteed compliance.")
            
            # Technology refresh analysis
            st.markdown("**Technology Refresh Timeline:**")
            tech_refresh_df = pd.DataFrame({
                "Year": list(range(0, ul+1, params['regulatory_update_frequency_years'])),
                "Cumulative Tech Improvement": [params['technology_evolution_rate'] * i for i in range(0, (ul // params['regulatory_update_frequency_years']) + 1)],
                "Update Required": ["Yes" if i > 0 else "Initial" for i in range(0, (ul // params['regulatory_update_frequency_years']) + 1)]
            })
            st.dataframe(tech_refresh_df, width='stretch')
        
        # Energy Cost Analysis
        if "annual_electricity_cost" in params:
            st.subheader("⚡ Energy Cost & Efficiency Analysis")
            col_e1, col_e2, col_e3 = st.columns(3)
            
            with col_e1:
                st.metric("Annual Electricity Cost", fmt(params['annual_electricity_cost']))
                st.metric("Annual Gas Cost", fmt(params['annual_gas_cost']))
                total_energy_cost = params['annual_electricity_cost'] + params['annual_gas_cost']
                st.metric("Total Energy Cost (Year 1)", fmt(total_energy_cost))
            
            with col_e2:
                st.metric("Electricity Tariff Increase", f"{params['electricity_tariff_increase']:.0f}%/year",
                         delta_color="inverse")
                st.metric("Gas Supply Interruptions", f"{params['gas_supply_interruption_days']} days/year")
                interruption_cost = params['gas_supply_interruption_days'] * params['production_downtime_cost']
                st.metric("Interruption Cost", fmt(interruption_cost))
            
            with col_e3:
                st.metric("Energy Efficiency Improvement", f"{params['energy_efficiency_improvement']:.0f}%/year")
                st.metric("Solar Integration Cost", fmt(params['solar_integration_cost']))
                st.metric("Solar Energy Offset", f"{params['solar_energy_offset']:.0f}%")
            
            # Calculate total energy-adjusted costs
            st.markdown("**Energy-Adjusted Total Cost of Ownership:**")
            
            energy_costs_buy = []
            energy_costs_lease = []
            
            for year in range(ul):
                # Electricity cost with tariff increase
                elec_cost = params['annual_electricity_cost'] * ((1 + params['electricity_tariff_increase']/100) ** year)
                
                # Apply efficiency improvements
                efficiency_factor = 1 - (params['energy_efficiency_improvement']/100 * year)
                elec_cost *= max(0.7, efficiency_factor)  # Cap at 30% improvement
                
                # For buy option: can integrate solar
                if year >= 2:  # Solar operational from year 2
                    elec_cost_buy = elec_cost * (1 - params['solar_energy_offset']/100)
                else:
                    elec_cost_buy = elec_cost
                
                # For lease: typically no solar integration
                elec_cost_lease = elec_cost
                
                energy_costs_buy.append(elec_cost_buy + params['annual_gas_cost'])
                energy_costs_lease.append(elec_cost_lease + params['annual_gas_cost'])
            
            total_energy_buy = sum(energy_costs_buy) + params['solar_integration_cost'] - params.get('govt_industrial_package_subsidy', 0)
            total_energy_lease = sum(energy_costs_lease)
            
            energy_comparison = pd.DataFrame({
                "Option": ["Buy (with Solar)", "Lease (Grid Only)", "Difference"],
                "Total Energy Cost": [total_energy_buy, total_energy_lease, total_energy_lease - total_energy_buy],
                "Average Annual": [total_energy_buy/ul, total_energy_lease/ul, (total_energy_lease - total_energy_buy)/ul]
            })
            
            st.dataframe(
                energy_comparison.style.format({
                    "Total Energy Cost": "₨{:,.2f}M",
                    "Average Annual": "₨{:,.2f}M"
                }),
                width='stretch'
            )
            
            energy_savings = total_energy_lease - total_energy_buy
            if energy_savings > 0:
                st.success(f"💡 **Energy Advantage (Buy):** Ownership enables solar integration, saving PKR {energy_savings:.0f}M over {ul} years ({(energy_savings/pp)*100:.1f}% of asset cost).")
            
            # Government subsidy highlight
            if params.get('govt_industrial_package_subsidy', 0) > 0:
                st.info(f"🏛️ **Government Support:** Industrial package provides PKR {params['govt_industrial_package_subsidy']:.0f}M subsidy for energy-efficient owned assets.")
            
            # Energy security score
            st.markdown("**Energy Security Assessment:**")
            security_score = (
                (100 - params['gas_supply_interruption_days']/365*100) * 0.4 +  # Supply reliability
                (params['solar_energy_offset']) * 0.3 +  # Energy independence
                (params['alternative_fuel_option_value']/pp*100) * 0.3  # Fuel flexibility
            )
            st.metric("Energy Security Score", f"{security_score:.0f}/100",
                     help="Based on supply reliability, energy independence, and fuel flexibility")
        
        # Islamic Finance & Cross-Border Analysis
        if "ijarah_profit_rate" in params:
            st.subheader("🕌 Islamic Finance & Cross-Border Analysis")
            
            # Financing comparison
            col_i1, col_i2, col_i3, col_i4 = st.columns(4)
            
            with col_i1:
                st.metric("Ijarah Profit Rate", f"{params['ijarah_profit_rate']:.1f}%")
                st.metric("Conventional Loan Rate", f"{params['conventional_loan_rate']:.1f}%",
                         delta=f"+{params['conventional_loan_rate'] - params['ijarah_profit_rate']:.1f}%",
                         delta_color="inverse")
            
            with col_i2:
                st.metric("Rate Advantage (Ijarah)", f"{params['conventional_loan_rate'] - params['ijarah_profit_rate']:.1f}%")
                rate_savings = pp * (params['conventional_loan_rate'] - params['ijarah_profit_rate'])/100
                st.metric("Annual Rate Savings", fmt(rate_savings))
            
            with col_i3:
                st.metric("USD/PKR Rate", f"{params['usd_pkr_rate']:.0f}")
                st.metric("Forex Volatility", f"{params['forex_volatility']:.0f}%/year",
                         delta_color="inverse")
            
            with col_i4:
                st.metric("Shariah Compliance Value", fmt(params['shariah_compliance_value']))
                st.metric("Reputational Premium", fmt(params['reputational_premium']))
            
            # Total cost comparison with forex risk
            st.markdown("---")
            st.markdown("**Comprehensive Cost Comparison:**")
            
            # Ijarah total cost (USD-denominated)
            ijarah_total_cost = lp * ul + params['political_risk_insurance_cost'] * ul + params['cross_border_transaction_cost']
            hedging_cost = pp * (params['hedging_cost_percentage']/100)
            ijarah_total_with_hedging = ijarah_total_cost + hedging_cost
            
            # Conventional loan total cost
            loan_annual_payment = pp * (params['conventional_loan_rate']/100)
            loan_total_cost = loan_annual_payment * ul + pp
            
            # Forex risk scenarios
            forex_stable = ijarah_total_with_hedging
            forex_5pct_depreciation = ijarah_total_with_hedging * 1.05
            forex_10pct_depreciation = ijarah_total_with_hedging * 1.10
            
            cost_comparison_df = pd.DataFrame({
                "Financing Option": [
                    "Islamic Ijarah (Hedged)",
                    "Islamic Ijarah (5% PKR depreciation)",
                    "Islamic Ijarah (10% PKR depreciation)",
                    "Conventional Loan (PKR)",
                    "**Cost Difference (Stable)**",
                    "**Cost Difference (10% depreciation)**"
                ],
                "Total Cost (PKR M)": [
                    forex_stable,
                    forex_5pct_depreciation,
                    forex_10pct_depreciation,
                    loan_total_cost,
                    loan_total_cost - forex_stable,
                    loan_total_cost - forex_10pct_depreciation
                ],
                "Effective Rate": [
                    f"{params['ijarah_profit_rate']:.1f}%",
                    f"{params['ijarah_profit_rate'] * 1.05:.1f}%",
                    f"{params['ijarah_profit_rate'] * 1.10:.1f}%",
                    f"{params['conventional_loan_rate']:.1f}%",
                    "—",
                    "—"
                ]
            })
            
            st.dataframe(
                cost_comparison_df.style.format({
                    "Total Cost (PKR M)": "₨{:,.2f}M"
                }),
                width='stretch'
            )
            
            # Recommendation
            cost_advantage_stable = loan_total_cost - forex_stable
            cost_advantage_worst = loan_total_cost - forex_10pct_depreciation
            
            col_rec1, col_rec2 = st.columns(2)
            
            with col_rec1:
                st.markdown("**Financial Analysis:**")
                if cost_advantage_stable > 0:
                    st.success(f"✅ **Ijarah is {cost_advantage_stable:.0f}M cheaper** (with hedging) despite forex risk")
                else:
                    st.warning(f"⚠️ **Conventional loan is {abs(cost_advantage_stable):.0f}M cheaper** in stable scenario")
                
                if cost_advantage_worst > 0:
                    st.info(f"💱 **Even with 10% PKR depreciation**, Ijarah is {cost_advantage_worst:.0f}M cheaper")
                else:
                    st.error(f"🚨 **With 10% PKR depreciation**, conventional loan becomes {abs(cost_advantage_worst):.0f}M cheaper")
            
            with col_rec2:
                st.markdown("**Strategic Considerations:**")
                shariah_total_value = params['shariah_compliance_value'] + params['reputational_premium']
                st.write(f"✅ **Shariah Compliance:** {fmt(shariah_total_value)} brand value")
                st.write(f"🏦 **Lessor Rating:** {params['middle_east_lessor_rating']} vs {params['local_bank_rating']}")
                st.write(f"💰 **Rate Advantage:** {params['conventional_loan_rate'] - params['ijarah_profit_rate']:.1f}% lower")
                
            # Final recommendation
            st.markdown("---")
            total_ijarah_advantage = cost_advantage_stable + shariah_total_value
            
            if total_ijarah_advantage > pp * 0.05:  # >5% of asset value
                st.success(f"""
                ### ✅ **Recommendation: Islamic Ijarah**
                
                **Financial:** {cost_advantage_stable:.0f}M cost savings + **Strategic:** {shariah_total_value:.0f}M brand value = **Total Advantage: {total_ijarah_advantage:.0f}M**
                
                The Ijarah structure offers:
                - {params['conventional_loan_rate'] - params['ijarah_profit_rate']:.1f}% lower profit rate
                - Shariah compliance enhances Fauji Foods' brand reputation
                - Access to Middle Eastern lessor ({params['middle_east_lessor_rating']} rated)
                - Hedging costs are offset by rate advantage
                
                **Risk Mitigation:** Implement forex hedging strategy ({params['hedging_cost_percentage']:.0f}% cost) and political risk insurance.
                """)
            elif cost_advantage_worst < 0:
                st.warning(f"""
                ### ⚠️ **Recommendation: Conventional Financing (with conditions)**
                
                While Ijarah offers brand value ({shariah_total_value:.0f}M), forex risk is significant. Consider:
                - Conventional loan is {abs(cost_advantage_worst):.0f}M cheaper in adverse scenario
                - PKR volatility ({params['forex_volatility']:.0f}%) creates substantial risk
                - Local bank relationship benefits
                
                **Alternative:** Negotiate PKR-denominated Ijarah with local Islamic bank if available.
                """)
            else:
                st.info(f"""
                ### 💡 **Balanced Decision**
                
                Both options are competitive. Decision factors:
                - **Choose Ijarah if:** Brand positioning and Shariah compliance are strategic priorities
                - **Choose Conventional if:** Forex risk aversion and cost certainty are priorities
                - **Consider:** Hybrid approach or PKR-denominated Islamic financing
                """)
            
            # Forex sensitivity chart
            st.markdown("**Forex Sensitivity Analysis:**")
            forex_scenarios = list(range(-5, 16, 5))
            ijarah_costs = [ijarah_total_with_hedging * (1 + pct/100) for pct in forex_scenarios]
            loan_costs = [loan_total_cost] * len(forex_scenarios)
            
            forex_chart = pd.DataFrame({
                "PKR Depreciation (%)": forex_scenarios,
                "Islamic Ijarah Cost": ijarah_costs,
                "Conventional Loan Cost": loan_costs
            }).set_index("PKR Depreciation (%)")
            
            st.line_chart(forex_chart)
        
        # Cash flow comparison chart
        st.markdown("---")
        st.subheader("💰 Cash Flow Comparison")
        
        years_scenario = list(range(0, ul + 1))
        cf_chart_scenario = pd.DataFrame({
            "Year": years_scenario,
            "Buy": buy_cf_scenario,
            "Lease": lease_cf_scenario
        }).set_index("Year")
        
        st.line_chart(cf_chart_scenario)
        
        # Cumulative cash flow
        st.subheader("📊 Cumulative Cash Flow Analysis")
        cumulative_buy = [sum(buy_cf_scenario[:i+1]) for i in range(len(buy_cf_scenario))]
        cumulative_lease = [sum(lease_cf_scenario[:i+1]) for i in range(len(lease_cf_scenario))]
        
        cumulative_df = pd.DataFrame({
            "Year": years_scenario,
            "Cumulative Buy": cumulative_buy,
            "Cumulative Lease": cumulative_lease
        }).set_index("Year")
        
        st.line_chart(cumulative_df)
        
        # Sensitivity Analysis
        st.markdown("---")
        st.subheader("🎚️ Sensitivity Analysis")
        
        st.markdown("**Impact of Discount Rate Changes on NPV:**")
        
        sensitivity_rates = [dr - 0.05, dr - 0.025, dr, dr + 0.025, dr + 0.05]
        sensitivity_results = []
        
        for rate in sensitivity_rates:
            npv_buy_sens = calculate_npv(rate, buy_cf_scenario)
            npv_lease_sens = calculate_npv(rate, lease_cf_scenario)
            nal_sens = npv_buy_sens - npv_lease_sens
            
            sensitivity_results.append({
                "Discount Rate": f"{rate*100:.1f}%",
                "NPV Buy": npv_buy_sens,
                "NPV Lease": npv_lease_sens,
                "NAL": nal_sens,
                "Recommendation": "Lease" if nal_sens > 0 else "Buy"
            })
        
        sensitivity_df = pd.DataFrame(sensitivity_results)
        st.dataframe(
            sensitivity_df.style.format({
                "NPV Buy": "₨{:,.2f}M",
                "NPV Lease": "₨{:,.2f}M",
                "NAL": "₨{:,.2f}M"
            }),
            width='stretch'
        )
        
        # Download scenario report
        st.markdown("---")
        scenario_report = pd.DataFrame([{
            "Scenario": scenario_choice,
            "Purchase Price": pp,
            "Useful Life": ul,
            "NPV (Buy)": npv_scenario_buy,
            "NPV (Lease)": npv_scenario_lease,
            "NAL": nal_scenario,
            "Recommendation": "Lease" if nal_scenario > 0 else "Buy",
            "Discount Rate": f"{dr*100}%",
            "Tax Rate": f"{tr*100}%"
        }])
        
        scenario_buffer = io.BytesIO()
        with pd.ExcelWriter(scenario_buffer, engine="xlsxwriter") as writer:
            scenario_report.to_excel(writer, index=False, sheet_name="Scenario Analysis")
            sensitivity_df.to_excel(writer, index=False, sheet_name="Sensitivity Analysis")
            cf_chart_scenario.to_excel(writer, sheet_name="Cash Flows")
        
        st.download_button(
            label=f"⬇️ Download {scenario_choice} Analysis Report",
            data=scenario_buffer.getvalue(),
            file_name=f"Fauji_Foods_{scenario_choice.replace(' ', '_')}_Analysis.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# ==============================
# FINAL REPORT DOWNLOAD
# ==============================
st.markdown("---")
st.subheader("📄 Final Report")

report_df = pd.concat([
    historic_df.assign(Section="Historical Financials"),
    impact_df.assign(Section="Financial Impact")
])

buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
    report_df.to_excel(writer, index=False, sheet_name="Lease vs Buy Report")

st.download_button(
    label="⬇️ Download Final Report (Excel)",
    data=buffer.getvalue(),
    file_name="Fauji_Foods_Lease_vs_Buy_Report.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# ==============================
# FOOTER
# ==============================
st.caption(
    f"Generated on {datetime.now().strftime('%d %B %Y')} | Strategic Finance Project – Fauji Foods Limited"
)
