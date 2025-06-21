from decimal import Decimal

import pytest

from app.models import User, Admin, Account, Payment


@pytest.mark.unit
class TestModels:
    """Unit тесты для моделей базы данных"""

    def test_user_model_creation(self):
        """Тест создания модели пользователя"""
        user = User(
            email="test@example.com",
            full_name="Test User",
            password_hash="hashed_password",
        )
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.password_hash == "hashed_password"

    def test_admin_model_creation(self):
        """Тест создания модели администратора"""
        admin = Admin(
            email="admin@example.com",
            full_name="Test Admin",
            password_hash="hashed_password",
        )
        assert admin.email == "admin@example.com"
        assert admin.full_name == "Test Admin"
        assert admin.password_hash == "hashed_password"

    def test_account_model_creation(self):
        """Тест создания модели счета"""
        account = Account(
            user_id=1,
            balance=Decimal("1000.50"),
        )
        assert account.user_id == 1
        assert account.balance == Decimal("1000.50")

    def test_payment_model_creation(self):
        """Тест создания модели платежа"""
        payment = Payment(
            transaction_id="test-transaction-123",
            user_id=1,
            account_id=1,
            amount=Decimal("100.00"),
        )
        assert payment.transaction_id == "test-transaction-123"
        assert payment.user_id == 1
        assert payment.account_id == 1
        assert payment.amount == Decimal("100.00")

    def test_account_balance_precision(self):
        """Тест точности баланса счета"""
        # Проверяем что Decimal правильно обрабатывает десятичные дроби
        account = Account(
            user_id=1,
            balance=Decimal("123.456789"),
        )
        assert account.balance == Decimal("123.456789")
        assert str(account.balance) == "123.456789"

    def test_payment_amount_precision(self):
        """Тест точности суммы платежа"""
        payment = Payment(
            transaction_id="test-precision",
            user_id=1,
            account_id=1,
            amount=Decimal("0.01"),
        )
        assert payment.amount == Decimal("0.01")

    def test_user_string_representation(self):
        """Тест строкового представления пользователя"""
        user = User(
            email="test@example.com",
            full_name="Test User",
            password_hash="hash",
        )
        user.id = 1
        # Проверяем что строковое представление содержит класс
        user_str = str(user)
        assert "User" in user_str
        # Базовое строковое представление SQLAlchemy модели содержит объект
        assert "object" in user_str
