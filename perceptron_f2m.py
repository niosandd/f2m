import pymorphy3
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


class Perceptron:
    def __init__(self, regression=False, C=1.0, eps=0, learning_rate=0.001, max_iter=1000,
                 random_state=0):
        self.regression = regression
        self.C = C
        self.eps = eps
        self.learning_rate = learning_rate
        self.max_iter = max_iter
        self.random_state = random_state

    def fit(self, X, y):
        if self.regression:
            self.bias, self.weights = self._find_weights(X, y)
        else:
            classes = np.unique(y)
            n_classes = len(classes)
            _, n_features = X.shape

            self.bias = np.zeros(n_classes)
            self.weights = np.zeros((n_classes, n_features))
            np.random.seed(self.random_state)

            for i, cls in enumerate(classes):
                y_binary = np.where(y == cls, 1, -1)
                self.bias[i], self.weights[i] = self._find_weights(X, y_binary)

    def _find_weights(self, X, y):
        n_samples, n_features = X.shape
        bias = 0
        weights = np.zeros(n_features) if self.regression else np.random.randn(n_features)

        for _ in range(self.max_iter):
            for i in range(n_samples):
                y_pred = X[i] @ weights + bias
                margin = y[i] - y_pred if self.regression else y[i] * y_pred
                condition = np.abs(margin) > self.eps if self.regression else margin < 1

                if condition:
                    if self.regression:
                        db = -self.C * (margin - self.eps)
                        dw = -self.C * (margin - self.eps) * X[i]
                    else:
                        db = -self.C * y[i]
                        dw = -self.C * y[i] * X[i]

                    bias -= self.learning_rate * db
                    weights -= self.learning_rate * dw

        return bias, weights

    def predict(self, X):
        scores = X @ self.weights.T + self.bias

        return scores if self.regression else np.argmax(scores, axis=1)


def perceptron_black_list(text):
    with open("perceptron_info.txt", encoding="UTF-8") as f:
        info = eval(f.read())
    morph = pymorphy3.MorphAnalyzer()
    categories = list(info.keys())
    clear_info = {}
    for category in categories:
        clear_info[category] = []
    morph_text = []
    for word in text:
        temp_word = morph.normal_forms(word)[0]
        morph_text.append(temp_word)
        for category in categories:
            if temp_word == morph.normal_forms(category)[0]:
                _ = clear_info.pop(category, None)

    for key in clear_info:
        for word in info[key]:
            temp_word = morph.normal_forms(word)[0]
            if temp_word not in morph_text:
                clear_info[key].append(word)
    answer = []
    for part in list(clear_info.values()):
        answer += part
    return answer


# Данные
words = [
    "Мясо", "Морепродукты", "Молочные продукты", "Овощи", "Зелень", "Фрукты и ягоды",
    "Макаронные изделия и крупы", "Хлебобулочные изделия", "Соусы и приправы", "Овощи и зелень",
    "Мясные продукты", "Мясная продукция", "Морские продукты", "Фрукты", "Ягоды", "Макароны",
    "Хлеб", "Соусы", "Приправы", "Яблоко", "Банан", "Груша", "Апельсин", "Молоко", "Сыр", "Хлеб",
    "Масло", "Колбаса", "Сосиска", "Картофель", "Помидор", "Огурец", "Капуста", "Рис", "Макароны",
    "Кофе", "Чай", "Сахар", "Соль", "Перец", "Тыква", "Шпинат", "Ананас", "Вишня", "Слива", "Манго", "Киви", "Лимон",
    "Миндаль", "Фисташки", "Грецкий орех", "Пекан", "Мёд", "Гречка", "Кускус", "Горчица",
    "Кетчуп", "Сметана", "Йогурт"
]
labels = [
    "Категория", "Категория", "Категория", "Категория", "Категория", "Категория", "Категория",
    "Категория", "Категория", "Категория", "Категория", "Категория", "Категория", "Категория",
    "Категория", "Категория", "Категория", "Категория", "Категория", "Не категория", "Не категория",
    "Не категория", "Не категория", "Не категория", "Не категория", "Не категория", "Не категория",
    "Не категория", "Не категория", "Не категория", "Не категория", "Не категория", "Не категория",
    "Не категория", "Не категория", "Не категория", "Не категория", "Не категория", "Не категория",
    "Не категория", "Не категория", "Не категория", "Не категория", "Не категория", "Не категория",
    "Не категория", "Не категория", "Не категория", "Не категория", "Не категория", "Не категория",
    "Не категория", "Не категория", "Не категория", "Не категория", "Не категория", "Не категория",
    "Не категория", "Не категория"
]

encoder = LabelEncoder()
X = encoder.fit_transform(words)
y = encoder.fit_transform(labels)
X_train, X_test, y_train, y_test = train_test_split(X.reshape(-1, 1), y, test_size=0.4, random_state=0)
linear_svc = Perceptron(random_state=0)
linear_svc.fit(X_train, y_train)
linear_svc_pred_res = linear_svc.predict(X_test)
linear_svc_accuracy = accuracy_score(y_test, linear_svc_pred_res)

print(f'LinearSVC accuracy: {linear_svc_accuracy:}')
print(linear_svc_pred_res)
print(linear_svc.weights, linear_svc.bias)
