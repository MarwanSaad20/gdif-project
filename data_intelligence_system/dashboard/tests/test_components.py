"""
test_components.py

اختبارات لوحدات مكونات الواجهة (components) باستخدام pytest.
"""

import pytest
from dashboard.components import charts, tables

def test_create_bar_chart():
    """
    اختبار إنشاء مكون رسم بياني من charts.py
    """
    dummy_data = {
        'labels': ['A', 'B', 'C'],
        'values': [10, 20, 30]
    }

    chart = charts.create_bar_chart("توزيع تجريبي", dummy_data['labels'], dummy_data['values'])

    assert chart is not None
    assert hasattr(chart, 'figure'), "العنصر العائد ليس رسمًا تفاعليًا صالحًا من نوع Graph"
    assert 'data' in chart.figure, "الرسم لا يحتوي على بيانات (data)"

def test_create_data_table():
    """
    اختبار إنشاء جدول تفاعلي من tables.py
    """
    dummy_data = [
        {'name': 'Alice', 'age': 30},
        {'name': 'Bob', 'age': 25},
    ]

    columns = [
        {"name": "الاسم", "id": "name"},
        {"name": "العمر", "id": "age"}
    ]

    # استخدام المعاملات المسماة لتفادي أخطاء الترتيب
    table = tables.create_data_table(
        data=dummy_data,
        columns=columns,
        id="جدول1"
    )

    assert table is not None
    assert hasattr(table, 'columns'), "الجدول لا يحتوي على خاصية الأعمدة"
    # التأكد من تطابق البيانات مع مراعاة أن table.data قد تكون نسخة
    assert list(table.data) == dummy_data, "بيانات الجدول لا تطابق البيانات الأصلية"
