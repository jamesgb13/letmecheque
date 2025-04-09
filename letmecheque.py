import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="LetMeCheque", layout="wide")

# --- Hide Streamlit footer/menu ---
hide_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
"""
st.markdown(hide_style, unsafe_allow_html=True)

# --- Sidebar Navigation ---
st.sidebar.title("💸 LetMeCheque")
st.sidebar.caption("Your Personal Finance Hub")

selected_tab = st.sidebar.radio("Navigate", [
    "🏠 Overview", 
    "💼 Balances", 
    "📍 Location Alerts", 
    "💡 Smart Advisor"
])

# --- Tab: Overview ---
if selected_tab == "🏠 Overview":
    st.header("📊 Average Student Monthly Spending Overview")

    csv_path = "Cleaned_Monthly_Spending.csv"


    try:
        df = pd.read_csv(csv_path)

        df.columns = [col.strip().replace("_()", "").replace("_", " ") for col in df.columns]

        month_order = ["January", "February", "March", "April", "May", "June",
                       "July", "August", "September", "October", "November", "December"]
        df["Month"] = pd.Categorical(df["Month"], categories=month_order, ordered=True)

        st.subheader("🔍 Filter by Spending Category")
        spending_categories = [col for col in df.columns if col not in ["Student ID", "Month", "Total"]]
        selected_category = st.selectbox("Choose a category:", ["Total"] + spending_categories)

        st.subheader(f"📈 Average Student Spending on {selected_category} Over Time")
        chart_data = df.groupby("Month")[selected_category].mean().reindex(month_order)
        st.line_chart(chart_data)

        max_month = chart_data.idxmax()
        max_value = chart_data.max()
        st.success(f"💡 You spent the most on **{selected_category}** in **{max_month}** (€{max_value:.2f})")

        if selected_category != "Total":
            from sklearn.linear_model import LinearRegression
            import numpy as np

            st.markdown("### 🔍 Regression Analysis + Forecast")
            st.caption("We use a simple linear regression model to project next month's spending.")

            df_forecast = df.groupby("Month")[selected_category].mean().reindex(month_order).dropna().reset_index()
            df_forecast["Month_Num"] = np.arange(len(df_forecast))

            X = df_forecast["Month_Num"].values.reshape(-1, 1)
            y = df_forecast[selected_category].values
            model = LinearRegression().fit(X, y)

            next_month_num = len(df_forecast)
            forecast_value = model.predict([[next_month_num]])[0]

            st.info(f"📈 Predicted spending on **{selected_category}** next month: **€{forecast_value:.2f}**")

            df_forecast["Predicted"] = model.predict(X)
            st.line_chart(df_forecast.set_index("Month")[[selected_category, "Predicted"]])

            # --- SIMULATION ---
            st.markdown("### 🎮 Simulate Extra Monthly Spending")
            st.caption("Use the slider to see how spending more on this category would affect the monthly totals.")

            sim_extra = st.slider(
                f"How much extra would you spend monthly on {selected_category}? (€)",
                min_value=0, max_value=500, value=0, step=10
            )

            simulated_chart = chart_data + sim_extra
            st.line_chart(simulated_chart)

            sim_max_month = simulated_chart.idxmax()
            sim_max_value = simulated_chart.max()
            st.info(f"📊 With the simulation, your highest spend on **{selected_category}** would be in **{sim_max_month}** at **€{sim_max_value:.2f}**.")

    except FileNotFoundError:
        st.error("❌ 'Cleaned_Monthly_Spending.csv' not found on your Desktop.")



# --- Tab: Balances ---
if selected_tab == "💼 Balances":
    st.header("💼 Balance Breakdown")

    col1, col2, col3 = st.columns(3)

    with col1:
        revolut_balance = st.number_input(
            "Revolut Balance", 
            min_value=0.0, 
            value=st.session_state.get("revolut_balance", 0.0), 
            step=1.0
        )
        st.session_state["revolut_balance"] = revolut_balance

    with col2:
        bank_balance = st.number_input(
            "Other Bank Balance", 
            min_value=0.0, 
            value=st.session_state.get("bank_balance", 0.0), 
            step=1.0
        )
        st.session_state["bank_balance"] = bank_balance

    with col3:
        cash_balance = st.number_input(
            "Cash on Hand", 
            min_value=0.0, 
            value=st.session_state.get("cash_balance", 0.0), 
            step=1.0
        )
        st.session_state["cash_balance"] = cash_balance

    total_balance = revolut_balance + bank_balance + cash_balance
    st.session_state["total_balance"] = total_balance

    st.write(f"**Total Available Balance:** €{total_balance:.2f}")

    if total_balance > 0:
        balance_df = pd.DataFrame({
            "Source": ["Revolut", "Other Bank", "Cash"],
            "Balance": [revolut_balance, bank_balance, cash_balance]
        })
        fig, ax = plt.subplots()
        ax.pie(balance_df["Balance"], labels=balance_df["Source"], autopct="%1.1f%%", startangle=90)
        ax.axis("equal")
        st.pyplot(fig)
    else:
        st.info("Enter some balances to generate a chart.")

# --- Tab: Location Alerts ---
if selected_tab == "📍 Location Alerts":
    st.header("📍 High-Spending Zone Advisor")

    location = st.selectbox("Where are you right now?", [
        "Home", "Work", "Shopping Mall", "Nightclub", "Concert", "Restaurant", "Grafton Street", "Temple Bar"
    ])

    high_spend_locations = [
        "Shopping Mall", "Nightclub", "Concert", "Restaurant", "Grafton Street", "Temple Bar"
    ]

    if location in high_spend_locations:
        st.warning(f"🚨 Heads up! {location} is known for high spending. Watch your wallet! 💳")
    else:
        st.success(f"✅ {location} is a low-risk spending zone. Good place to stay frugal!")

# --- Tab: Smart Advisor ---
if selected_tab == "💡 Smart Advisor":
    st.header("💡 Smart Spending Advisor")

    st.markdown("### 📦 Most Expensive Platforms by Category")
    st.caption("These platforms have the highest average spend per user — based on student shopping data.")

    platform_path = "final_irish_online_shopping_50.csv"

    try:
        df_platform = pd.read_csv(platform_path)

        df_platform = df_platform[["Website", "Category", "Avg_Spending_Per_User (\x80)"]]
        df_platform = df_platform.rename(columns={
            "Website": "Platform",
            "Category": "Category",
            "Avg_Spending_Per_User (\x80)": "Avg Spend/User (€)"
        })
        df_platform = df_platform.sort_values("Avg Spend/User (€)", ascending=False)

        styled_table = df_platform.style\
            .format({"Avg Spend/User (€)": "€{:.2f}"})\
            .hide(axis="index")

        st.dataframe(styled_table, use_container_width=True)

    except FileNotFoundError:
        st.error("❌ 'final_irish_online_shopping_50.csv' not found on your Desktop.")
    except KeyError as e:
        st.error(f"❌ Missing expected column: {e}")

    # --- Weekly Financial Risk Checker (10% of Total Balance) ---
    st.markdown("### 🧮 Weekly Financial Risk Checker")
    st.caption("If you're planning to spend more than 10% of your total available balance, you're at risk of overspending.")

    weekly_expense_estimate = st.slider("Estimated Weekly Spending (€)", 0, 1000, 300)

    total_balance = st.session_state.get("total_balance", 0)

    if total_balance > 0:
        spending_ratio = (weekly_expense_estimate / total_balance) * 100
        if spending_ratio > 10:
            st.error(f"🔴 You're planning to spend {spending_ratio:.1f}% of your total balance — that’s too high!")
        else:
            st.success(f"🟢 You're spending just {spending_ratio:.1f}% of your total balance. You’re in a safe zone.")
    else:
        st.info("ℹ️ Enter your balances in the '💼 Balances' tab to get a risk assessment.")

# --- Footer ---
st.markdown("---")
st.caption("LetMeCheque | Built to keep your finances on track 💼📈")

