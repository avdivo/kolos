# Текущий общий алгоритм работы программы

1. Пользователь вводит команду в терминале (main.py).
2. Если это выход из программы, то обнуляются сигналы всех точек (main.py).
3. Команда обрабатывается как текст. Слово разбивается на буквы (handler.py).
4. Каждая буква обрабатывается алгоритмом класса PointManager (ai_engine.py).
5. По окончании обработки слова сигналы всех точек уменьшаются на 0.1 (ai_engine.py).
