import pytest
from handler import handle_text
from memory import InOut
from service import initialize_database, clear_db

in_out = InOut()


@pytest.fixture(scope='session', autouse=True)
def setup_database():
    # Инициализируем базу данных перед выполнением тестов
    initialize_database()
    yield
    # Очищаем базу данных после выполнения всех тестов
    clear_db()


def parse_input_data(input_data):
    # Разбиваем входную строку на пары вопрос-ответ
    pairs = input_data.split(' | ')
    parsed_pairs = []
    for pair in pairs:
        question, answer = pair.split(' -> ')
        parsed_pairs.append((question.strip(), answer.strip()))
    return parsed_pairs


# Параметризованный тест для функции handle_text
@pytest.mark.parametrize("input_data", [
    "a b -> Нет данных | b c -> Нет данных | a -> Пробел | Пустой ввод -> b",
    # Добавьте больше тестовых случаев по мере необходимости
])
def test_handle_text(input_data):
    # Разбираем входную строку на пары вопрос-ответ
    pairs = parse_input_data(input_data)

    for question, expected_answer in pairs:
        # Вызываем функцию handle_text с вопросом
        result = handle_text(in_out.convertor(in_str=question))

        # Проверяем, что результат соответствует ожидаемому ответу
        assert in_out.convertor(out_str=result) == expected_answer
