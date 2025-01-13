import string
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict

import requests
import matplotlib.pyplot as plt


def get_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Перевірка на помилки HTTP
        return response.text
    except requests.RequestException as e:
        return None


def map_function(word: str):
    return word.lower(), 1


def remove_punctuation(text):
    return text.translate(str.maketrans("", "", string.punctuation))


def shuffle_function(mapped_values):
    shuffled = defaultdict(list)
    for key, value in mapped_values:
        shuffled[key].append(value)
    return shuffled.items()


def reduce_function(key_values):
    key, values = key_values
    return key, sum(values)


# Виконання MapReduce
def map_reduce(text, search_words=None):
    # Видалення знаків пунктуації
    text = remove_punctuation(text)
    words = text.split()

    # Якщо задано список слів для пошуку, враховувати тільки ці слова
    if search_words:
        words = [word for word in words if word in search_words]

    # Паралельний Мапінг
    with ThreadPoolExecutor() as executor:
        mapped_values = list(executor.map(map_function, words))

    # Крок 2: Shuffle
    shuffled_values = shuffle_function(mapped_values)

    # Паралельна Редукція
    with ThreadPoolExecutor() as executor:
        reduced_values = list(executor.map(reduce_function, shuffled_values))

    return dict(reduced_values)


def count_top_words(reduced_data, top=10):
    # Відображення слів за спаданням кількості зустрічей
    top_words = {}
    sorted_result = sorted(reduced_data.items(), key=lambda x: x[1])
    for word, count in sorted_result[-top:]:
        top_words[word] = count
    return top_words


def visualize_top_words(reduced_data, top=10):
    plt.figure(figsize=(8, 6))
    top_words = count_top_words(reduced_data, top)
    plt.barh(list(top_words.keys()), list(top_words.values()))
    plt.barh(top_words.keys(), top_words.values())
    plt.xlabel("Count")
    plt.ylabel("Words")
    plt.title(f"Top {top} Words")
    plt.show()


if __name__ == "__main__":
    url = "https://gutenberg.net.au/ebooks01/0100021.txt"
    data = get_text(url)
    if data:
        # Виконання MapReduce на вхідному тексті
        # search_words = ["war", "peace", "love", "freedom"]
        result = map_reduce(data)
        visualize_top_words(result, top=20)

    else:
        print("Помилка: Не вдалося отримати вхідний текст.")
