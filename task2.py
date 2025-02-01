import json
import time
import gzip
from datasketch import HyperLogLog


def extract_ip_from_json(line):
    try:
        log_entry = json.loads(line)
        return log_entry.get('remote_addr', '')
    except json.JSONDecodeError:
        return ''


def load_and_process_log(filepath):
    ips = []
    invalid = 0
    total = 0

    is_gzipped = filepath.endswith('.gz')

    open_func = gzip.open if is_gzipped else open
    mode = 'rt' if is_gzipped else 'r'

    with open_func(filepath, mode, encoding='utf-8') as file:
        for line in file:
            total += 1
            ip = extract_ip_from_json(line.strip())
            if ip:
                ips.append(ip.encode('utf-8'))
            else:
                invalid += 1

    print(f"Оброблено рядків: {total}")
    print(f"Некоректних рядків: {invalid}")
    return ips

def exact_count(ips):
    start_time = time.time()
    unique_count = len(set(ips))
    execution_time = time.time() - start_time
    return unique_count, execution_time


def hll_count(ips):
    start_time = time.time()
    hll = HyperLogLog(14)
    for ip in ips:
        hll.update(ip)
    count = hll.count()
    execution_time = time.time() - start_time
    return count, execution_time


def print_results(exact_result, hll_result):
    exact_count, exact_time = exact_result
    hll_count, hll_time = hll_result

    print("\nРезультати порівняння:")
    print("-" * 50)
    print(f"{'Метрика':<25} {'Точний підрахунок':>15} {'HyperLogLog':>15}")
    print("-" * 50)
    print(f"{'Унікальні елементи':<25} {exact_count:>15.1f} {hll_count:>15.1f}")
    print(f"{'Час виконання (сек.)':<25} {exact_time:>15.6f} {hll_time:>15.6f}")
    print("-" * 50)

    # Розрахунок відносної похибки
    error = abs(exact_count - hll_count) / exact_count * 100
    print(f"\nВідносна похибка HyperLogLog: {error:.2f}%")


if __name__ == "__main__":
    log_filepath = "lms-stage-access.log.gz"

    try:
        print("Завантаження та обробка файлу...")
        ip_addresses = load_and_process_log(log_filepath)

        if not ip_addresses:
            print("Не знайдено жодної коректної IP-адреси в файлі.")
            exit(1)

        print(f"\nЗнайдено IP-адрес: {len(ip_addresses)}")

        print("\nВиконання точного підрахунку...")
        exact_result = exact_count(ip_addresses)

        print("Виконання підрахунку HyperLogLog...")
        hll_result = hll_count(ip_addresses)

        print_results(exact_result, hll_result)

    except FileNotFoundError:
        print(f"Помилка: Файл '{log_filepath}' не знайдено")
    except Exception as e:
        print(f"Помилка при виконанні: {e}")