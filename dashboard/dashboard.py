import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

#untuk menyiapkan orders_daily_df
def create_orders_daily_df(df):
    orders_daily_df = df.resample(rule='D', on='order_approved_at').agg({
        "order_id": "nunique"
    })
    orders_daily_df = orders_daily_df.reset_index()
    orders_daily_df.rename(columns={
        "order_id": "order_count"
    }, inplace=True)
    
    return orders_daily_df

#untuk menyiapkan bycity_df
def create_bycity_df(df):
    bycity_df = df.groupby(by="customer_city").customer_id.nunique().reset_index()
    bycity_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    
    return bycity_df

#untuk menyiapkan bystate_df
def create_bystate_df(df):
    bystate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    
    return bystate_df

#untuk menyiapkan customer_monthly_df
def create_customer_monthly_df(df):
    customer_monthly_df = df.resample(rule='ME', on='order_purchase_timestamp').agg({
        "customer_id": "nunique"
    })
    customer_monthly_df.index = customer_monthly_df.index.strftime('%B')
    
    customer_monthly_df = customer_monthly_df.reset_index()
    customer_monthly_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    
    return customer_monthly_df

#untuk menyiapkan order_monthly_df
def create_order_monthly_df(df):
    order_monthly_df = df.resample(rule='ME', on='order_purchase_timestamp').agg({
        "order_id": "nunique"
    })
    order_monthly_df.index = order_monthly_df.index.strftime('%B')
    
    order_monthly_df = order_monthly_df.reset_index()
    order_monthly_df.rename(columns={
        "order_id": "order_count"
    }, inplace=True)
    
    return order_monthly_df

#load berkas main_data.csv
main_data = pd.read_csv("dashboard/main_data.csv")

#mengurutkan data frame berdasarkan order_approved_at
datetime_columns = ["order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date",
"order_delivered_customer_date", "order_estimated_delivery_date"]
main_data.sort_values(by="order_approved_at", inplace=True)
main_data.reset_index(inplace=True)
 
for colum in datetime_columns:
    main_data[colum] = pd.to_datetime(main_data[colum])

#membuat filter dengan widget date input dan menambahkan logo perusahaan pada sidebar
min_date = main_data["order_approved_at"].min()
max_date = main_data["order_approved_at"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("dashboard/logo.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

#data yang difilter disimpan di main_df
main_df = main_data[(main_data["order_approved_at"] >= str(start_date)) & 
                (main_data["order_approved_at"] <= str(end_date))]

#helper function yang telah dibuat sebelumnya
orders_daily_df = create_orders_daily_df(main_df)
bycity_df = create_bycity_df(main_df)
bystate_df = create_bystate_df(main_df)
customer_monthly_df = create_customer_monthly_df(main_df)
order_monthly_df = create_order_monthly_df(main_df)

#menambahkan header pada dashboard
st.header('E Commerce Public Dashboard :sparkles:')

#menampilkan informasi total order dan revenue dalam bentuk metric
st.subheader('Daily Orders')

col1 = st.columns(1)[0] 

with col1:
    total_orders = orders_daily_df.order_count.sum()
    st.metric("Total orders", value=total_orders)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    orders_daily_df["order_approved_at"],
    orders_daily_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

#dua visualisasi data untuk menampilkan demografi customer
st.subheader("Demografi Pelanggan")

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(20, 10))
    plt.plot(customer_monthly_df["order_purchase_timestamp"], customer_monthly_df["customer_count"], marker='o', linewidth=2, color="#72BCD4") 
    ax.set_title("Jumlah Pelanggan berdasarkan Kota", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)
    
with col2:
    fig, ax = plt.subplots(figsize=(20, 10))
    colors_ = ["#72BCD4"] + ["#D3D3D3"] * (len(bystate_df) - 1)
    sns.barplot(
        x="customer_count", 
        y="customer_state",
        data=bystate_df.sort_values(by="customer_count", ascending=False).head(10),
        palette=colors_,
        ax=ax
    )
    ax.set_title("Jumlah Pelanggan berdasarkan State", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)

#dua visualisasi data untuk menampilkan performa penjualan
st.subheader("Performa Penjualan Bulanan")

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(20, 10))
    colors_ = ["#72BCD4"] + ["#D3D3D3"] * (len(bystate_df) - 1)
    sns.lineplot(
        x="", 
        y="customer_state",
        data=bystate_df.sort_values(by="customer_count", ascending=False).head(10),
        palette=colors_,
        ax=ax
    )
    ax.set_title("Jumlah Pelanggan berdasarkan State", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)
    
with col2:
    fig, ax = plt.subplots(figsize=(20, 10))
    plt.plot(order_monthly_df["order_purchase_timestamp"], order_monthly_df["order_count"], marker='o', linewidth=2, color="#72BCD4")
    plt.title("Jumlah Order per-Bulan", loc="center", fontsize=20)
    plt.xticks(fontsize=10) 
    plt.yticks(fontsize=10) 
    plt.show()