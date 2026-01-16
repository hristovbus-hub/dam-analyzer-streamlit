import itertools
import numpy as np

TOTAL_QH = 11  # 2 часа и 45 минути

def generate_combinations(total):
    combos = []

    # 1 период
    combos.append([total])

    # 2 периода
    for a in range(1, total):
        b = total - a
        combos.append([a, b])

    # 3 периода
    for a in range(1, total - 1):
        for b in range(1, total - a):
            c = total - a - b
            combos.append([a, b, c])

    return combos


def find_best_periods(prices):
    best_avg = -1
    best_result = None

    combos = generate_combinations(TOTAL_QH)

    for combo in combos:
        # пример: combo = [3, 4, 4]
        # трябва да намерим най-добрите позиции за тези дължини

        # всички възможни стартови позиции за първия период
        for starts in itertools.combinations(range(len(prices)), len(combo)):
            # проверка за валидност (да не се застъпват)
            valid = True
            periods = []
            current_end = -1

            for length, start in zip(combo, starts):
                end = start + length
                if start <= current_end:
                    valid = False
                    break
                if end > len(prices):
                    valid = False
                    break
                periods.append((start, end))
                current_end = end

            if not valid:
                continue

            # изчисляваме средната цена
            total_sum = sum(np.sum(prices[s:e]) for s, e in periods)
            avg_price = total_sum / TOTAL_QH

            if avg_price > best_avg:
                best_avg = avg_price
                best_result = periods

    return best_result, best_avg
