import streamlit as st
import pandas as pd
from itertools import combinations

st.title("DAM Analyzer – Топ 3 периода (общо 3 часа)")

def qh_to_time(qh):
    minutes = (qh - 1) * 15
    h = minutes // 60
    m = minutes % 60
    return f"{h:02d}:{m:02d}"

def interval_to_time(start, end):
    return qh_to_time(start), qh_to_time(end + 1)

def load_prices_from_csv(uploaded_file):
    prices = {}
    df = pd.read_csv(uploaded_file, sep=None, engine="python")
    for _, row in df.iterrows():
        if isinstance(row["Продукт"], str) and row["Продукт"].startswith("QH"):
            qh = int(row["Продукт"].split()[1])
            price = float(str(row["Цена (EUR/MWh)"]).replace(",", "."))
            prices[qh] = price
    return prices

def all_intervals(prices):
    intervals = []
    qhs = sorted(prices.keys())
    for start in qhs:
        for end in qhs:
            if end >= start:
                interval = list(range(start, end + 1))
                avg_price = sum(prices[q] for q in interval) / len(interval)
                intervals.append((start, end, len(interval), avg_price))
    return intervals

def find_best_three(intervals):
    best = None
    for a, b, c in combinations(intervals, 3):
        total_len = a[2] + b[2] + c[2]
        if total_len == 12:
            # check no overlap
            if max(a[0], b[0], c[0]) > min(a[1], b[1], c[1]):
                total_avg = (a[3]*a[2] + b[3]*b[2] + c[3]*c[2]) / 12
                if best is None or total_avg > best[0]:
                    best = (total_avg, a, b, c)
    return best

uploaded_file = st.file_uploader("📤 Качи DAM CSV файл", type=["csv"])

if uploaded_file:
    prices = load_prices_from_csv(uploaded_file)
    intervals = all_intervals(prices)
    best = find_best_three(intervals)

    if best:
        total_avg, a, b, c = best

        st.subheader(f"📊 Обща средна цена: **{total_avg:.2f} EUR/MWh**")

        for idx, interval in enumerate([a, b, c], start=1):
            start, end, length, avg = interval
            start_time, end_time = interval_to_time(start, end)

            st.markdown(f"""
            ### 🔹 Период {idx}
            - QH: **{start} → {end}**
            - Часове: **{start_time} – {end_time}**
            - Продължителност: **{length} QH**
            - Средна цена: **{avg:.2f} EUR/MWh**
            """)
    else:
        st.error("❌ Не може да се намери комбинация от 3 периода с общо 12 QH.")
