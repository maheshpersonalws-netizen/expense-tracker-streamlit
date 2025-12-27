import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ---------- Session State Initialization ----------
if 'expenses' not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Description'])

# ---------- Expense Functions ----------
def add_expense(date, category, amount, description):
    new_expense = pd.DataFrame([[date, category, amount, description]],
                               columns=st.session_state.expenses.columns)
    st.session_state.expenses = pd.concat([st.session_state.expenses, new_expense], ignore_index=True)

def load_expenses():
    uploaded_file = st.file_uploader("Choose a file", type=['csv'], key='file_upload')
    if uploaded_file is not None:
        st.session_state.expenses = pd.read_csv(uploaded_file)
        st.success("Expenses loaded!")

def save_expenses():
    st.session_state.expenses.to_csv('expenses.csv', index=False)
    st.success("Expenses saved successfully!")

def visualize_expenses():
    if not st.session_state.expenses.empty:
        fig, ax = plt.subplots()
        sns.barplot(data=st.session_state.expenses, x='Category', y='Amount', ax=ax)
        plt.xticks(rotation=45)
        st.pyplot(fig)
    else:
        st.warning("No expenses to visualize!")

def monthly_summary():
    st.subheader("📊 Monthly Summary")
    if st.session_state.expenses.empty:
        st.info("No data to show summary.")
        return

    df = st.session_state.expenses.copy()
    df['Date'] = pd.to_datetime(df['Date'])
    df['Month'] = df['Date'].dt.to_period('M').astype(str)

    monthly_total = df.groupby('Month')['Amount'].sum().reset_index()
    st.line_chart(monthly_total.set_index('Month'))

    top_category = df.groupby('Category')['Amount'].sum().idxmax()
    avg_monthly = monthly_total['Amount'].mean()

    st.markdown(f"**Top Spending Category:** {top_category}")
    st.markdown(f"**Average Monthly Spend:** ₹{avg_monthly:.2f}")

def budget_alert():
    st.subheader("💸 Budget Alert System")
    budget = st.number_input("Set your monthly budget (₹)", min_value=0.0, value=10000.0, step=500.0, key='budget_input')

    if not st.session_state.expenses.empty:
        df = st.session_state.expenses.copy()
        df['Date'] = pd.to_datetime(df['Date'])
        df['Month'] = df['Date'].dt.to_period('M').astype(str)
        latest_month = df['Month'].max()
        latest_total = df[df['Month'] == latest_month]['Amount'].sum()

        if latest_total > budget:
            st.error(f"⚠️ Budget Exceeded for {latest_month}: ₹{latest_total:.2f} (Over by ₹{latest_total - budget:.2f})")
        else:
            st.success(f"✅ You are within budget for {latest_month}: ₹{latest_total:.2f}")

# ---------- Main App ----------
st.set_page_config(page_title="Gigglade Expense Tracker", layout="wide")

st.sidebar.header('📁 File Operations')
if st.sidebar.button('💾 Save Expenses', key='sidebar_save'):
    save_expenses()
if st.sidebar.button('📂 Load Expenses', key='sidebar_load'):
    load_expenses()

st.sidebar.header("🔍 Navigation")
option = st.sidebar.radio("Go to", ["Add Expense", "Load/Save", "Visualize", "Monthly Summary", "Budget Alert"], key='main_nav')

st.title("💼 Expense Tracker with Smart Features")

if option == "Add Expense":
    st.header("➕ Add New Expense")
    date = st.date_input("Date", key='main_date')
    category = st.selectbox("Category", ["Food", "Transport", "Bills", "Entertainment", "Other"], key='main_category')
    amount = st.number_input("Amount", min_value=0.0, format="%.2f", key='main_amount')
    description = st.text_input("Description", key='main_description')

    if st.button("Add Expense", key='main_add'):
        add_expense(date, category, amount, description)
        st.success("Expense added!")

elif option == "Load/Save":
    st.header("📁 Load / Save Expenses")
    load_expenses()
    if st.button("💾 Save Expenses", key='main_save'):
        save_expenses()

elif option == "Visualize":
    st.header("📊 Expense Visualization")
    visualize_expenses()

elif option == "Monthly Summary":
    monthly_summary()

elif option == "Budget Alert":
    budget_alert()

st.header('🧾 All Expenses')
st.write(st.session_state.expenses)
