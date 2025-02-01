import mmh3


class BloomFilter:
    def __init__(self, size, num_hashes):
        if size <= 0 or num_hashes <= 0:
            raise ValueError("Розмір та кількість хеш-функцій мають бути додатними числами")

        self.size = size
        self.num_hashes = num_hashes
        self.bit_array = [0] * size

    def _get_hash(self, item):
        hash_values = []
        for seed in range(self.num_hashes):
            hash_value = mmh3.hash(str(item), seed) % self.size
            hash_values.append(abs(hash_value))
        return hash_values

    def add(self, item):
        if not item or not isinstance(item, str):
            raise ValueError("Елемент має бути непорожнім рядком")

        for bit_position in self._get_hash(item):
            self.bit_array[bit_position] = 1

    def check(self, item):
        if not item or not isinstance(item, str):
            raise ValueError("Елемент має бути непорожнім рядком")

        return all(self.bit_array[bit_position] for bit_position in self._get_hash(item))


def check_password_uniqueness(bloom_filter, passwords):
    if not isinstance(bloom_filter, BloomFilter):
        raise TypeError("Перший аргумент має бути екземпляром BloomFilter")
    if not isinstance(passwords, list):
        raise TypeError("Другий аргумент має бути списком")

    results = {}
    for password in passwords:
        try:
            if bloom_filter.check(password):
                results[password] = "вже використаний"
            else:
                results[password] = "унікальний"
                bloom_filter.add(password)
        except ValueError as e:
            results[password] = f"помилка: {str(e)}"
    return results


if __name__ == "__main__":
    bloom = BloomFilter(size=1000, num_hashes=3)

    existing_passwords = ["password123", "admin123", "qwerty123"]
    for password in existing_passwords:
        bloom.add(password)

    new_passwords_to_check = ["password123", "newpassword", "admin123", "guest"]
    results = check_password_uniqueness(bloom, new_passwords_to_check)

    for password, status in results.items():
        print(f"Пароль '{password}' — {status}.")