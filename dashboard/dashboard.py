import os

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="E-Commerce Dashboard", page_icon="🛒", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@st.cache_data
def load_data():
    main = pd.read_csv(
        os.path.join(BASE_DIR, "main_data.csv"),
        parse_dates=["order_purchase_timestamp"],
    )
    rfm = pd.read_csv(os.path.join(BASE_DIR, "rfm_data.csv"))
    return main, rfm


main_df, rfm_df = load_data()

# ---------------------------------------------------------------- Sidebar
st.sidebar.header("Filter")
min_date = main_df["order_purchase_timestamp"].min().date()
max_date = main_df["order_purchase_timestamp"].max().date()

date_range = st.sidebar.date_input(
    "Rentang tanggal pembelian",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if not (isinstance(date_range, (tuple, list)) and len(date_range) == 2):
    st.info("Pilih tanggal awal dan tanggal akhir pada filter di sidebar.")
    st.stop()

start_date, end_date = date_range
df = main_df[
    (main_df["order_purchase_timestamp"] >= pd.to_datetime(start_date))
    & (main_df["order_purchase_timestamp"] < pd.to_datetime(end_date) + pd.Timedelta(days=1))
].copy()

if df.empty:
    st.warning("Tidak ada data pada rentang tanggal tersebut.")
    st.stop()

df["purchase_month"] = df["order_purchase_timestamp"].dt.to_period("M").astype(str)
order_level = df.drop_duplicates("order_id")

# ---------------------------------------------------------------- Header
st.title("🛒 E-Commerce Dashboard")
st.caption("Pesanan berstatus delivered. Revenue dihitung dari harga produk (R$), tidak termasuk ongkos kirim.")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Pesanan", f"{order_level['order_id'].nunique():,}")
c2.metric("Total Revenue", f"R$ {df['revenue'].sum():,.0f}")
c3.metric("Rata-rata Review", f"{order_level['review_score'].mean():.2f}")
c4.metric("Pesanan Terlambat", f"{order_level['is_late'].mean() * 100:.1f}%")

# ---------------------------------------------------------------- Pertanyaan 1
st.header("Revenue per Kategori Produk")

cat = (
    df.groupby("product_category_name_english")["revenue"].sum().sort_values(ascending=False)
)
n_cat = st.slider("Jumlah kategori yang ditampilkan", 3, 10, 5)
top, bottom = cat.head(n_cat), cat.tail(n_cat)

col1, col2 = st.columns(2)
with col1:
    fig, ax = plt.subplots(figsize=(7, 4))
    colors = ["#1f77b4"] + ["#c7c7c7"] * (len(top) - 1)
    ax.barh(top.index[::-1], (top / 1e6)[::-1], color=colors[::-1])
    ax.set_title(f"{n_cat} Kategori Revenue Tertinggi")
    ax.set_xlabel("Revenue (juta R$)")
    st.pyplot(fig)
with col2:
    fig, ax = plt.subplots(figsize=(7, 4))
    colors = ["#d62728"] + ["#c7c7c7"] * (len(bottom) - 1)
    ax.barh(bottom.index[::-1], (bottom / 1e6)[::-1], color=colors)
    ax.set_title(f"{n_cat} Kategori Revenue Terendah")
    ax.set_xlabel("Revenue (juta R$)")
    st.pyplot(fig)

st.subheader("Tren Revenue Bulanan")
monthly = df.groupby("purchase_month")["revenue"].sum().reset_index()
fig, ax = plt.subplots(figsize=(12, 4))
ax.plot(monthly["purchase_month"], monthly["revenue"] / 1e6, marker="o", color="#1f77b4")
ax.set_xlabel("Bulan")
ax.set_ylabel("Revenue (juta R$)")
ax.tick_params(axis="x", rotation=45)
st.pyplot(fig)

# ---------------------------------------------------------------- Pertanyaan 2
st.header("Keterlambatan Pengiriman per State")

min_orders = st.slider("Minimal jumlah pesanan per state", 10, 500, 100, step=10)
state = (
    order_level.groupby("customer_state")
    .agg(
        total_orders=("order_id", "nunique"),
        late_pct=("is_late", lambda x: x.mean() * 100),
        avg_review=("review_score", "mean"),
    )
    .reset_index()
)
state = state[state["total_orders"] >= min_orders].sort_values("late_pct", ascending=False)

if state.empty:
    st.warning("Tidak ada state yang memenuhi batas minimal pesanan.")
else:
    col3, col4 = st.columns(2)
    with col3:
        top_late = state.head(10)
        national = order_level["is_late"].mean() * 100
        fig, ax = plt.subplots(figsize=(7, 4))
        colors = (["#d62728"] * 3 + ["#c7c7c7"] * 7)[: len(top_late)]
        ax.barh(top_late["customer_state"][::-1], top_late["late_pct"][::-1], color=colors[::-1])
        ax.axvline(national, color="black", linestyle="--", linewidth=1,
                   label=f"Rata-rata ({national:.1f}%)")
        ax.set_title("State dengan Keterlambatan Tertinggi")
        ax.set_xlabel("Pesanan terlambat (%)")
        ax.legend()
        st.pyplot(fig)
    with col4:
        review_late = order_level.groupby("is_late")["review_score"].mean()
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.bar(["Tepat waktu", "Terlambat"],
               [review_late.get(False, 0), review_late.get(True, 0)],
               color=["#1f77b4", "#d62728"])
        ax.set_ylim(0, 5)
        ax.set_title("Rata-rata Skor Review")
        ax.set_ylabel("Skor review (1-5)")
        st.pyplot(fig)

# ---------------------------------------------------------------- RFM
st.header("Analisis RFM")
st.caption("RFM dihitung dari seluruh data transaksi delivered (tidak terpengaruh filter tanggal).")

col5, col6 = st.columns(2)
with col5:
    seg = rfm_df["segment"].value_counts()
    fig, ax = plt.subplots(figsize=(7, 4))
    colors = ["#d62728" if s == "At Risk (Nilai Tinggi)" else "#c7c7c7" for s in seg.index]
    ax.barh(seg.index[::-1], seg.values[::-1], color=colors[::-1])
    ax.set_title("Jumlah Pelanggan per Segmen")
    ax.set_xlabel("Jumlah pelanggan")
    st.pyplot(fig)
with col6:
    st.metric("Rata-rata Recency (hari)", f"{rfm_df['recency'].mean():.0f}")
    st.metric("Rata-rata Frequency", f"{rfm_df['frequency'].mean():.2f}")
    st.metric("Rata-rata Monetary (R$)", f"{rfm_df['monetary'].mean():,.0f}")

st.subheader("Top 5 Pelanggan")
tab1, tab2, tab3 = st.tabs(["Recency", "Frequency", "Monetary"])
cols = ["customer_unique_id", "recency", "frequency", "monetary", "segment"]
with tab1:
    st.dataframe(rfm_df.sort_values("recency").head(5)[cols], hide_index=True)
with tab2:
    st.dataframe(rfm_df.sort_values("frequency", ascending=False).head(5)[cols], hide_index=True)
with tab3:
    st.dataframe(rfm_df.sort_values("monetary", ascending=False).head(5)[cols], hide_index=True)
