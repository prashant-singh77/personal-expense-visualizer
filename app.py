import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ---------- App Configuration ----------
st.set_page_config(page_title="💰 Personal Expense Visualizer", layout="wide")

# ---------- Title ----------
st.title("💰 Personal Expense Visualizer")
st.markdown("Upload your CSV to analyze expenses by category and over time.")

# ---------- Sidebar Upload ----------
st.sidebar.header("📂 Upload CSV")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type=["csv"])

@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Month'] = df['Date'].dt.to_period('M').astype(str)
    return df

if uploaded_file:
    try:
        df = load_data(uploaded_file)
    except Exception:
        st.error("⚠️ Could not read the file. Please upload a valid CSV with columns: Date, Category, Amount.")
        st.stop()

    if not {'Date', 'Category', 'Amount'}.issubset(df.columns):
        st.error("⚠️ CSV must contain 'Date', 'Category', and 'Amount' columns.")
        st.stop()

    # Remove rows with missing important values
    df.dropna(subset=['Date', 'Category', 'Amount'], inplace=True)

    # ---------- Sidebar Filters ----------
    st.sidebar.header("🔍 Filters")

    # Category filter
    categories = df['Category'].unique()
    selected_categories = st.sidebar.multiselect("Select categories", categories, default=categories)

    # Date range filter — ✅ fixed for user-friendly behavior
    min_date = df['Date'].min()
    max_date = df['Date'].max()
    default_range = [min_date, max_date]

    date_range = st.sidebar.date_input("Select date range", default_range, min_value=min_date, max_value=max_date)

    if (
        isinstance(date_range, list) and len(date_range) == 2
    ) or (
        isinstance(date_range, tuple) and len(date_range) == 2
    ):
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    else:
        st.warning("⚠️ Please select both start and end dates from the date picker.")
        st.stop()

    # ---------- Apply Filters ----------
    filtered_df = df[
        (df['Category'].isin(selected_categories)) &
        (df['Date'] >= start_date) &
        (df['Date'] <= end_date)
    ]

    # ---------- Data Preview ----------
    st.subheader("📄 Preview of Filtered Data")
    if not filtered_df.empty:
        show_all = st.checkbox("Show full table", value=False)

        if show_all:
           st.dataframe(filtered_df)
        else:
           st.dataframe(filtered_df.head())
        # ---------- Stats Summary ----------
        st.subheader("📈 Summary Statistics")

        total_spent = filtered_df['Amount'].sum()
        average_spent = filtered_df['Amount'].mean()

        col1, col2 = st.columns(2)
        col1.metric("💸 Total Spent", f"₹{total_spent:,.2f}")
        col2.metric("📊 Average per Entry", f"₹{average_spent:,.2f}")

        # ---------- Download Button ----------
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Download Filtered Data", data=csv, file_name="filtered_expenses.csv", mime='text/csv')

    else:
        st.info("ℹ️ No data found for selected filters.")
        st.stop()

    # ---------- Pie Chart ----------
    st.subheader("📊 Expense Distribution by Category")
    try:
        category_summary = filtered_df.groupby('Category')['Amount'].sum()
        if not category_summary.empty:
            fig1, ax1 = plt.subplots()
            ax1.pie(category_summary, labels=category_summary.index, autopct='%1.1f%%', startangle=90)
            ax1.axis('equal')
            st.pyplot(fig1)
        else:
            st.info("ℹ️ No category data to display.")
    except Exception:
        st.warning("⚠️ Could not generate pie chart. Please check the data format.")

    # ---------- Bar Chart ----------
    st.subheader("📈 Monthly Expense Trend")
    try:
        monthly_summary = filtered_df.groupby('Month')['Amount'].sum().reset_index()
        if not monthly_summary.empty:
            fig2, ax2 = plt.subplots()
            ax2.bar(monthly_summary['Month'], monthly_summary['Amount'], color='skyblue')
            ax2.set_title("Total Expenses Per Month")
            ax2.set_xlabel("Month")
            ax2.set_ylabel("Amount Spent (₹)")

            plt.xticks(rotation=45)
            st.pyplot(fig2)
        else:
            st.info("ℹ️ No monthly trend to show.")
    except Exception:
        st.warning("⚠️ Could not generate bar chart. Please check the data.")
else:
    st.info("👈 Upload a CSV file with columns: Date, Category, Amount.")
