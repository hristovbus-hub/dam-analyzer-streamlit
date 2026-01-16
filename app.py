import streamlit as st
import pandas as pd
import numpy as np
import itertools
import os

st.set_page_config(page_title="IBEX Оптимизатор", layout="centered")

st.title("📊 Резултати по блокове")
st.write("Най-скъпите 2 часа и 45 минути, групирани по периоди.")

uploaded_file = st.file_uploader(
    "Избери файл",
    type=['csv', 'txt', 'xls', 'xlsx'],
    accept_multiple_files=False
)

# ---------------------------------------------------------
# НОВИЯТ АЛГОРИТЪМ ЗА 1, 2 ИЛИ 3 ПЕРИОДА (ОБЩО 11 QH)
# ---------------------------------------------------------

TOTAL_QH = 11  # 2 часа и 45 минути

def generate_length_combinations(total):
    combos = []

    # 1 период
    combos.append([total])

    # 2 периода
    for a in range(1, total):
        combos.append([a, total - a])

    # 3 периода
    for a in range(1, total - 1):
        for b in range(1, total - a):
            c = total - a - b
            combos.append([a, b, c])

    return combos


def best_positions_for_lengths(prices, lengths):
    n = len(prices)
    k = len(lengths)

    best_avg = -1
    best_periods = None

    for starts in itertools.combinations(range(n), k):
        valid = True
        periods = []
        last_end = -1

        for start, length in zip(starts, lengths):
            end = start + length
            if start <= last_end or end > n:
                valid = False
                break
            periods.append((start, end))
            last_end = end

        if not valid:
            continue

        total_sum = sum(np.sum(prices[s:e]) for s, e in periods)
        avg = total_sum / TOTAL_QH

        if avg > best_avg:
            best_avg = avg
            best_periods = periods

    return best_periods, best_avg


def find_best_periods(prices):
    best_avg = -1
    best_periods = None

    combos = generate_length_combinations(TOTAL_QH)

    for lengths in combos:
        periods, avg = best_positions_for_lengths(prices, lengths)
        if periods is not None and avg > best_avg:
            best_avg = avg
            best_periods = periods

    return best_periods, best_avg


def format_periods(periods, df):
    output = []
    for i, (s, e) in enumerate(periods, start=1):
        start_time = df.loc[s, "Период на доставка"].split("-")[0].strip()
        end_time = df.loc[e - 1, "Период на доставка"].split("-")[1].strip()
        output.append(f"Период {i}: {start_time} – {end_time}")
    return "\n".join(output)


# ---------------------------------------------------------
# ЧЕТЕНЕ НА ФАЙЛА
# ---------------------------------------------------------

if uploaded_file is not None:
    try:
        ext = os.path.splitext(uploaded_file.name)[1].lower()

        if ext in ['.csv', '.txt']:
            df = pd.read_csv(uploaded_file, sep=';', skiprows=9)
        elif ext == '.xls':
            df = pd.read_excel(uploaded_file, skiprows=9, engine='xlrd')
        elif ext == '.xlsx':
            df = pd.read_excel(uploaded_file, skiprows=9, engine='openpyxl')
        else:
            st.error("Неподдържан файлов формат.")
            st.stop()

        df.columns = [c.strip() for c in df.columns]

        df = df[df['Продукт'].astype(str).str.startswith('QH')].copy()

        if df['Цена (EUR/MWh)'].dtype == object:
            df['Цена (EUR/MWh)'] = (
                df['Цена (EUR/MWh)']
                .astype(str)
                .str.replace(',', '.')
                .astype(float)
            )

        df['QH'] = df['Продукт'].str.extract(r'QH\s*(\d+)').astype(int)
        df = df.sort_values('QH').reset_index(drop=True)

        prices = df['Цена (EUR/MWh)'].to_numpy()

        # ---------------------------------------------------------
        # ТУК СЕ ИЗВИКВА НОВИЯТ АЛГОРИТЪМ
        # ---------------------------------------------------------
        periods, avg_price = find_best_periods(prices)

        st.subheader("⏳ Най-добър вариант:")

        st.text(format_periods(periods, df))

        st.success(f"Обща средна цена: {avg_price:.2f} EUR/MWh")

        st.line_chart(df.set_index('Период на доставка')['Цена (EUR/MWh)'])

    except Exception as e:
        st.error(f"Грешка: {e}")
