import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ---------- Page Config ----------
st.set_page_config(page_title="Gigglade Expense Tracker", layout="wide")

# ---------- Session State Initialization ----------
if 'expenses' not in st.session_state:
    st.session_state.expenses = pd.DataFrame(
        columns=['Date', 'Category', 'Amount', 'Description']
    )

# ---------- Expense Functions ----------
def add_expense(date, category, amount, description):
    new_expense = pd.DataFrame(
        [[date, category, amount, description]],
        columns=st.session_state.expenses.columns
    )
    st.session_state.expenses = pd.concat(
        [st.session_state.expenses, new_expense],
        ignore_index=True
    )

def load_expenses():
    uploaded_file = st.file_uploader(
        "Upload Expenses CSV",
        type=['csv']
    )
    if uploaded_file is not None:
        st.session_state.expenses = pd.read_csv(uploaded_file)
        st.success("Expenses loaded successfully!")

def save_expenses():
    if st.session_state.expenses.empty:
        st.warning("No expenses to download!")
        return

    csv = st.session_state.expenses.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download Expenses CSV",
        data=csv,
        file_name="expenses.csv",
        mime="text/csv"
    )

def visualize_expenses():
    if st.session_state.expenses.empty:
        st.warning("No expenses to visualize!")
        return

    fig, ax = plt.subplots()
    sns.barplot(
        data=st.session_state.expenses,
        x='Category',
        y='Amount',
        ax=ax
    )
    plt.xticks(rotation=45)
    st.pyplot(fig)

def monthly_summary():
    st.subheader("📊 Monthly Summary")

    if st.session_state.expenses.empty:
        st.info("No data available.")
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

    budget = st.number_input(
        "Set Monthly Budget (₹)",
        min_value=0.0,
        value=10000.0,
        step=500.0
    )

    if st.session_state.expenses.empty:
        st.info("No expense data available.")
        return

    df = st.session_state.expenses.copy()
    df['Date'] = pd.to_datetime(df['Date'])
    df['Month'] = df['Date'].dt.to_period('M').astype(str)

    latest_month = df['Month'].max()
    latest_total = df[df['Month'] == latest_month]['Amount'].sum()

    if latest_total > budget:
        st.error(
            f"⚠️ Budget Exceeded for {latest_month}: "
            f"₹{latest_total:.2f} "
            f"(Over by ₹{latest_total - budget:.2f})"
        )
    else:
        st.success(
            f"✅ Within Budget for {latest_month}: "
            f"₹{latest_total:.2f}"
        )

# ---------- Sidebar ----------
st.sidebar.header("🔍 Navigation")
option = st.sidebar.radio(
    "Go to",
    ["Add Expense", "Load / Save", "Visualize", "Monthly Summary", "Budget Alert"]
)

# ---------- Main UI ----------
st.title("💼 Expense Tracker (Streamlit Cloud Ready)")

if option == "Add Expense":
    st.header("➕ Add New Expense")

    date = st.date_input("Date")
    category = st.selectbox(
        "Category",
        ["Food", "Transport", "Bills", "Entertainment", "Other"]
    )
    amount = st.number_input("Amount (₹)", min_value=0.0, format="%.2f")
    description = st.text_input("Description")

    if st.button("Add Expense"):
        add_expense(date, category, amount, description)
        st.success("Expense added successfully!")

elif option == "Load / Save":
    st.header("📁 Load / Save Expenses")
    load_expenses()
    save_expenses()

elif option == "Visualize":
    st.header("📊 Expense Visualization")
    visualize_expenses()

elif option == "Monthly Summary":
    monthly_summary()

elif option == "Budget Alert":
    budget_alert()

# ---------- Display All Expenses ----------
st.header("🧾 All Expenses")
st.dataframe(st.session_state.expenses, use_container_width=True)
