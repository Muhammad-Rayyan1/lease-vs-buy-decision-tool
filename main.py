import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ================================
# CORE FINANCIAL FUNCTIONS
# ================================

def calculate_npv(cash_flows, rate):
    return sum(cf / ((1 + rate) ** year) for year, cf in enumerate(cash_flows))


def buy_cash_flows(data):
    depreciation = (data["purchase_price"] - data["residual_value"]) / data["useful_life"]
    tax_shield = depreciation * data["tax_rate"]
    flows = [-data["purchase_price"]]

    for _ in range(data["useful_life"]):
        after_tax_maint = data["maintenance"] * (1 - data["tax_rate"])
        flows.append(tax_shield - after_tax_maint)

    flows[-1] += data["residual_value"]
    return flows


def lease_cash_flows(data):
    flows = [0]
    for _ in range(data["useful_life"]):
        tax_shield = data["lease_payment"] * data["tax_rate"]
        flows.append(-(data["lease_payment"] - tax_shield))
    return flows


# ================================
# STREAMLIT UI SETUP
# ================================

st.set_page_config(
    page_title="Lease vs Buy Decision Tool",
    layout="wide"
)

st.title("💼 Lease vs Buy Decision Analyzer")
st.markdown("### AI-Based Financial Decision Support System")
st.markdown(
    "This interactive tool helps management decide whether to **LEASE or BUY** a capital-intensive asset using advanced financial analysis."
)

# ================================
# SIDEBAR INPUTS
# ================================

st.sidebar.header("🔢 Financial Inputs")

data = {
    "purchase_price": st.sidebar.number_input("Asset Purchase Price (PKR million)", 0.0, value=500.0),
    "useful_life": st.sidebar.number_input("Useful Life (Years)", 1, step=1, value=10),
    "residual_value": st.sidebar.number_input("Residual Value (PKR million)", 0.0, value=50.0),
    "maintenance": st.sidebar.number_input("Annual Maintenance Cost (PKR million)", 0.0, value=15.0),
    "lease_payment": st.sidebar.number_input("Annual Lease Payment (PKR million)", 0.0, value=70.0),
    "tax_rate": st.sidebar.slider("Corporate Tax Rate (%)", 0, 50, 29) / 100,
    "discount_rate": st.sidebar.slider("Discount Rate (%)", 0, 30, 15) / 100
}

st.markdown("---")

# ================================
# BUTTONS SECTION
# ================================

col1, col2, col3 = st.columns(3)

buy_flows = buy_cash_flows(data)
lease_flows = lease_cash_flows(data)

if col1.button("📈 Buy Cash Flows"):
    df = pd.DataFrame({"Year": range(len(buy_flows)), "Cash Flow": buy_flows})
    st.subheader("Buy Option – Cash Flows")
    st.table(df)

if col2.button("📈 Lease Cash Flows"):
    df = pd.DataFrame({"Year": range(len(lease_flows)), "Cash Flow": lease_flows})
    st.subheader("Lease Option – Cash Flows")
    st.table(df)

if col3.button("📊 Compare NPVs"):
    npv_buy = calculate_npv(buy_flows, data["discount_rate"])
    npv_lease = calculate_npv(lease_flows, data["discount_rate"])
    nal = npv_lease - npv_buy

    st.subheader("NPV Comparison")
    st.metric("NPV (Buy)", f"{npv_buy:.2f}")
    st.metric("NPV (Lease)", f"{npv_lease:.2f}")
    st.metric("NAL", f"{nal:.2f}")

    if nal > 0:
        st.success("✅ FINAL DECISION: LEASE")
    else:
        st.error("❌ FINAL DECISION: BUY")

st.markdown("---")

# ================================
# GRAPHS SECTION
# ================================

st.subheader("📊 Cash Flow Comparison Graph")

fig, ax = plt.subplots()
ax.plot(buy_flows, label="Buy Option", marker="o")
ax.plot(lease_flows, label="Lease Option", marker="o")
ax.set_xlabel("Year")
ax.set_ylabel("Cash Flow (PKR million)")
ax.set_title("Buy vs Lease Cash Flow Comparison")
ax.legend()
ax.grid(True)

st.pyplot(fig)

# ================================
# REPORT GENERATOR
# ================================

st.markdown("---")

if st.button("📄 Generate Full Financial Report"):
    npv_buy = calculate_npv(buy_flows, data["discount_rate"])
    npv_lease = calculate_npv(lease_flows, data["discount_rate"])
    nal = npv_lease - npv_buy
    decision = "LEASE" if nal > 0 else "BUY"

    report_text = f"""
LEASE VS BUY DECISION REPORT

Asset Purchase Price: PKR {data['purchase_price']} million
Useful Life: {data['useful_life']} years
Residual Value: PKR {data['residual_value']} million
Annual Maintenance Cost: PKR {data['maintenance']} million
Annual Lease Payment: PKR {data['lease_payment']} million

Tax Rate: {data['tax_rate']*100:.1f}%
Discount Rate: {data['discount_rate']*100:.1f}%

NPV (Buy Option): PKR {npv_buy:.2f} million
NPV (Lease Option): PKR {npv_lease:.2f} million
Net Advantage to Leasing (NAL): PKR {nal:.2f} million

FINAL RECOMMENDATION: {decision}

Decision Basis:
- Tax-adjusted cash flows
- Net Present Value (NPV) comparison
- Risk and financial efficiency analysis
"""

    st.subheader("📄 Generated Financial Report")
    st.text_area("Report Output", report_text, height=350)

    st.download_button(
        label="⬇️ Download Report",
        data=report_text,
        file_name="Lease_vs_Buy_Report.txt",
        mime="text/plain"
    )
