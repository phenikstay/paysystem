#!/usr/bin/env python3
"""
Утилита для быстрого интеграционного тестирования API платежной системы

Этот скрипт дополняет структурированные pytest тесты и предназначен для:
- Быстрой проверки работоспособности API после изменений
- Демонстрации возможностей API
- Smoke testing в продакшене
- Отладки HTTP запросов

Требует запущенный сервер на http://localhost:8000
"""

import hashlib
import os
import sys
import time
from decimal import Decimal
from pathlib import Path

# Настройка путей для корректной работы в PyCharm и других IDE
current_file_path = Path(__file__).resolve()
project_root = current_file_path.parent.parent
os.chdir(project_root)

# Добавляем корень проекта в PYTHONPATH если его там нет
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

print(f"🔧 Рабочая директория: {os.getcwd()}")
print(f"🔧 Корень проекта: {project_root}")
print(f"🐍 Python интерпретатор: {sys.executable}")

import requests

BASE_URL = "http://localhost:8000"
REQUEST_TIMEOUT = 30  # Увеличенный таймаут для Docker


# ANSI цвета для красивого вывода
class Colors:
    """Класс с ANSI кодами цветов для терминального вывода"""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    END = "\033[0m"


def print_header(title):
    """Печать заголовка секции"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}🔧 {title}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")


def print_test_result(test_name, status_code, expected_code, details=None):
    """Печать результата теста"""
    if status_code == expected_code:
        status = f"{Colors.GREEN}✅ УСПЕШНО{Colors.END}"
    else:
        status = f"{Colors.RED}❌ ОШИБКА{Colors.END}"

    print(f"{status} {test_name} (код: {status_code})")
    if details:
        print(f"   📋 {details}")


def print_summary(passed, total):
    """Печать итоговой сводки"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}📊 ИТОГОВАЯ СВОДКА{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")

    if passed == total:
        print(f"{Colors.GREEN}🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ: {passed}/{total}{Colors.END}")
        print(f"{Colors.GREEN}✨ Система работает отлично!{Colors.END}")
    else:
        print(f"{Colors.YELLOW}⚠️  ПРОЙДЕНО: {passed}/{total}{Colors.END}")
        print(f"{Colors.RED}❌ ПРОВАЛЕНО: {total-passed}/{total}{Colors.END}")


def check_user_auth():
    """Тестирование авторизации пользователя"""
    print_header("АВТОРИЗАЦИЯ ПОЛЬЗОВАТЕЛЯ")

    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/user/login",
            json={"email": "user@example.com", "password": "userpassword"},
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code == 200:
            data = response.json()
            token = data["access_token"]
            print_test_result(
                "Авторизация пользователя",
                response.status_code,
                200,
                f"JWT токен получен ({token[:20]}...)",
            )
            return token, True
        else:
            print_test_result(
                "Авторизация пользователя",
                response.status_code,
                200,
                f"Ошибка: {response.text}",
            )
            return None, False

    except Exception as e:
        print_test_result("Авторизация пользователя", 0, 200, f"Исключение: {str(e)}")
        return None, False


def check_admin_auth():
    """Тестирование авторизации администратора"""
    print_header("АВТОРИЗАЦИЯ АДМИНИСТРАТОРА")

    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/admin/login",
            json={"email": "admin@example.com", "password": "adminpassword"},
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code == 200:
            data = response.json()
            token = data["access_token"]
            print_test_result(
                "Авторизация администратора",
                response.status_code,
                200,
                f"JWT токен получен ({token[:20]}...)",
            )
            return token, True
        else:
            print_test_result(
                "Авторизация администратора",
                response.status_code,
                200,
                f"Ошибка: {response.text}",
            )
            return None, False

    except Exception as e:
        print_test_result("Авторизация администратора", 0, 200, f"Исключение: {str(e)}")
        return None, False


def check_user_endpoints(token):
    """Тестирование эндпоинтов пользователя"""
    print_header("ПОЛЬЗОВАТЕЛЬСКИЕ API")
    headers = {"Authorization": f"Bearer {token}"}
    passed = 0
    total = 3

    # Получение данных о себе
    try:
        response = requests.get(
            f"{BASE_URL}/api/users/me", headers=headers, timeout=REQUEST_TIMEOUT
        )
        if response.status_code == 200:
            data = response.json()
            print_test_result(
                "Получение профиля пользователя",
                response.status_code,
                200,
                f"ID: {data.get('id')}, Email: {data.get('email')}",
            )
            passed += 1
        else:
            print_test_result(
                "Получение профиля пользователя", response.status_code, 200
            )
    except Exception as e:
        print_test_result(
            "Получение профиля пользователя", 0, 200, f"Исключение: {str(e)}"
        )

    # Получение счетов
    try:
        response = requests.get(
            f"{BASE_URL}/api/users/me/accounts",
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )
        if response.status_code == 200:
            accounts = response.json()
            balance = accounts[0]["balance"] if accounts else 0
            print_test_result(
                "Получение счетов пользователя",
                response.status_code,
                200,
                f"Найдено счетов: {len(accounts)}, Баланс: {balance} руб.",
            )
            passed += 1
        else:
            print_test_result(
                "Получение счетов пользователя", response.status_code, 200
            )
    except Exception as e:
        print_test_result(
            "Получение счетов пользователя", 0, 200, f"Исключение: {str(e)}"
        )

    # Получение платежей
    try:
        response = requests.get(
            f"{BASE_URL}/api/users/me/payments",
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )
        if response.status_code == 200:
            payments = response.json()
            total_sum = sum(float(p["amount"]) for p in payments)
            print_test_result(
                "Получение истории платежей",
                response.status_code,
                200,
                f"Найдено платежей: {len(payments)}, Общая сумма: {total_sum:.2f} руб.",
            )
            passed += 1
        else:
            print_test_result("Получение истории платежей", response.status_code, 200)
    except Exception as e:
        print_test_result("Получение истории платежей", 0, 200, f"Исключение: {str(e)}")

    return passed, total


def check_admin_endpoints(token):
    """Тестирование эндпоинтов администратора"""
    print_header("АДМИНИСТРАТИВНЫЕ API")
    headers = {"Authorization": f"Bearer {token}"}
    passed = 0
    total = 2

    # Получение данных о себе
    try:
        response = requests.get(
            f"{BASE_URL}/api/admin/me", headers=headers, timeout=REQUEST_TIMEOUT
        )
        if response.status_code == 200:
            data = response.json()
            print_test_result(
                "Получение профиля администратора",
                response.status_code,
                200,
                f"ID: {data.get('id')}, Email: {data.get('email')}",
            )
            passed += 1
        else:
            print_test_result(
                "Получение профиля администратора", response.status_code, 200
            )
    except Exception as e:
        print_test_result(
            "Получение профиля администратора", 0, 200, f"Исключение: {str(e)}"
        )

    # Получение списка пользователей
    try:
        response = requests.get(
            f"{BASE_URL}/api/admin/users", headers=headers, timeout=REQUEST_TIMEOUT
        )
        if response.status_code == 200:
            users = response.json()
            print_test_result(
                "Получение списка пользователей",
                response.status_code,
                200,
                f"Найдено пользователей: {len(users)}",
            )
            passed += 1
        else:
            print_test_result(
                "Получение списка пользователей", response.status_code, 200
            )
    except Exception as e:
        print_test_result(
            "Получение списка пользователей", 0, 200, f"Исключение: {str(e)}"
        )

    return passed, total


def generate_signature(
    account_id, amount, transaction_id, user_id, secret_key="gfdmhghif38yrf9ew0jkf32"
):
    """Генерация подписи для вебхука"""
    if isinstance(amount, Decimal):
        amount_str = str(amount)
    else:
        amount_str = str(Decimal(str(amount)))

    data_string = f"{account_id}{amount_str}{transaction_id}{user_id}{secret_key}"
    return hashlib.sha256(data_string.encode()).hexdigest()


def check_webhook():
    """Тестирование вебхука"""
    print_header("СИСТЕМА ПЛАТЕЖЕЙ (ВЕБХУКИ)")
    passed = 0
    total = 3

    # Тест с валидной подписью
    transaction_id = str(time.time())
    user_id = 1
    account_id = 1
    amount = Decimal("150.50")

    amount_as_will_be_received = Decimal(str(float(amount)))
    signature = generate_signature(
        account_id, amount_as_will_be_received, transaction_id, user_id
    )

    webhook_data = {
        "transaction_id": transaction_id,
        "user_id": user_id,
        "account_id": account_id,
        "amount": float(amount),
        "signature": signature,
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/webhooks/payment",
            json=webhook_data,
            timeout=REQUEST_TIMEOUT,
        )
        if response.status_code == 200:
            print_test_result(
                "Обработка валидного вебхука",
                response.status_code,
                200,
                f"Платеж обработан, сумма: {amount} руб.",
            )
            passed += 1
        else:
            print_test_result("Обработка валидного вебхука", response.status_code, 200)
    except Exception as e:
        print_test_result(
            "Обработка валидного вебхука", 0, 200, f"Исключение: {str(e)}"
        )

    # Тест с невалидной подписью
    webhook_data["signature"] = "invalid_signature"
    try:
        response = requests.post(
            f"{BASE_URL}/api/webhooks/payment",
            json=webhook_data,
            timeout=REQUEST_TIMEOUT,
        )
        if response.status_code == 400:
            print_test_result(
                "Отклонение невалидной подписи",
                response.status_code,
                400,
                "Подпись корректно отклонена",
            )
            passed += 1
        else:
            print_test_result(
                "Отклонение невалидной подписи", response.status_code, 400
            )
    except Exception as e:
        print_test_result(
            "Отклонение невалидной подписи", 0, 400, f"Исключение: {str(e)}"
        )

    # Тест дублирующейся транзакции
    webhook_data["signature"] = signature
    try:
        response = requests.post(
            f"{BASE_URL}/api/webhooks/payment",
            json=webhook_data,
            timeout=REQUEST_TIMEOUT,
        )
        if response.status_code == 409:
            print_test_result(
                "Защита от дублирования транзакций",
                response.status_code,
                409,
                "Дублирующаяся транзакция корректно отклонена",
            )
            passed += 1
        else:
            print_test_result(
                "Защита от дублирования транзакций", response.status_code, 409
            )
    except Exception as e:
        print_test_result(
            "Защита от дублирования транзакций", 0, 409, f"Исключение: {str(e)}"
        )

    return passed, total


def check_admin_user_management(token):
    """Тестирование управления пользователями"""
    print_header("УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ")
    headers = {"Authorization": f"Bearer {token}"}
    passed = 0
    total = 3

    # Создание пользователя с уникальным email
    timestamp = str(int(time.time()))
    new_user_data = {
        "email": f"testuser{timestamp}@example.com",
        "full_name": "Test User Created",
        "password": "testpassword123",
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/admin/users",
            headers=headers,
            json=new_user_data,
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code == 201:
            user_data = response.json()
            user_id = user_data["id"]
            print_test_result(
                "Создание пользователя",
                response.status_code,
                201,
                f"Пользователь создан с ID: {user_id}",
            )
            passed += 1

            # Обновление пользователя
            update_data = {"full_name": "Updated Test User"}
            try:
                response = requests.put(
                    f"{BASE_URL}/api/admin/users/{user_id}",
                    headers=headers,
                    json=update_data,
                    timeout=REQUEST_TIMEOUT,
                )
                if response.status_code == 200:
                    print_test_result(
                        "Обновление пользователя",
                        response.status_code,
                        200,
                        "Данные пользователя обновлены",
                    )
                    passed += 1
                else:
                    print_test_result(
                        "Обновление пользователя", response.status_code, 200
                    )
            except Exception as e:
                print_test_result(
                    "Обновление пользователя", 0, 200, f"Исключение: {str(e)}"
                )

            # Удаление пользователя
            try:
                response = requests.delete(
                    f"{BASE_URL}/api/admin/users/{user_id}",
                    headers=headers,
                    timeout=REQUEST_TIMEOUT,
                )
                if response.status_code == 200:
                    print_test_result(
                        "Удаление пользователя",
                        response.status_code,
                        200,
                        "Пользователь успешно удален",
                    )
                    passed += 1
                else:
                    print_test_result(
                        "Удаление пользователя", response.status_code, 200
                    )
            except Exception as e:
                print_test_result(
                    "Удаление пользователя", 0, 200, f"Исключение: {str(e)}"
                )
        else:
            print_test_result(
                "Создание пользователя",
                response.status_code,
                201,
                f"Ошибка: {response.text}",
            )
    except Exception as e:
        print_test_result("Создание пользователя", 0, 201, f"Исключение: {str(e)}")

    return passed, total


def main():
    """Основная функция тестирования"""
    print(f"{Colors.BOLD}{Colors.PURPLE}")
    print("🚀 ИНТЕГРАЦИОННОЕ ТЕСТИРОВАНИЕ ПЛАТЕЖНОЙ СИСТЕМЫ")
    print("=" * 60)
    print(f"📍 Базовый URL: {BASE_URL}")
    print(f"🕐 Время запуска: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{Colors.END}")

    total_passed = 0
    total_tests = 0

    # Проверяем доступность сервера
    try:
        response = requests.get(f"{BASE_URL}/", timeout=REQUEST_TIMEOUT)
        print(f"{Colors.GREEN}✅ Сервер доступен{Colors.END}")
    except requests.exceptions.ConnectionError:
        print(
            f"{Colors.RED}❌ Сервер недоступен. Убедитесь, что приложение запущено.{Colors.END}"
        )
        print(
            f"{Colors.YELLOW}💡 Из терминала запустите: python3 -m app.main{Colors.END}"
        )
        print(
            f"{Colors.YELLOW}💡 Или из PyCharm: запустите app/main.py напрямую{Colors.END}"
        )
        print(
            f"{Colors.CYAN}🔗 Сервер должен быть доступен по адресу: {BASE_URL}{Colors.END}"
        )
        return
    except Exception as e:
        print(f"{Colors.RED}❌ Ошибка подключения: {str(e)}{Colors.END}")
        print(
            f"{Colors.YELLOW}💡 Проверьте, что сервер запущен на порту 8000{Colors.END}"
        )
        return

    # Тестирование авторизации
    user_token, user_auth_success = check_user_auth()
    admin_token, admin_auth_success = check_admin_auth()

    total_tests += 2
    if user_auth_success:
        total_passed += 1
    if admin_auth_success:
        total_passed += 1

    # Тестирование пользовательских эндпоинтов
    if user_token:
        passed, total = check_user_endpoints(user_token)
        total_passed += passed
        total_tests += total

    # Тестирование административных эндпоинтов
    if admin_token:
        passed, total = check_admin_endpoints(admin_token)
        total_passed += passed
        total_tests += total

        passed, total = check_admin_user_management(admin_token)
        total_passed += passed
        total_tests += total

    # Тестирование вебхука
    passed, total = check_webhook()
    total_passed += passed
    total_tests += total

    # Итоговая сводка
    print_summary(total_passed, total_tests)

    if total_passed == total_tests:
        print(
            f"\n{Colors.GREEN}{Colors.BOLD}🎯 РЕЗУЛЬТАТ: Система готова к работе!{Colors.END}"
        )
    else:
        print(
            f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  РЕЗУЛЬТАТ: Требуется внимание к проблемным тестам{Colors.END}"
        )


if __name__ == "__main__":
    main()
