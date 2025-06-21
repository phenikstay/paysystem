"""Общие утилиты для приложения"""

from datetime import datetime
from decimal import Decimal


def custom_json_serializer(obj):
    """Кастомный сериализатор для JSON"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
