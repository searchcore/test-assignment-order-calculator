from decimal import Decimal

import pytest

from src.domain.order_quantity import (
    InvalidInvariant,
    calc_available_quantity,
    calc_coverage_period,
    calc_target_stock,
    calc_to_order_amount,
)

DAYS_TO_COVER = 7


def calc_order(stock, daily_sales, incoming, lead_days, safety_stock) -> int:
    period = calc_coverage_period(lead_days, DAYS_TO_COVER)
    target = calc_target_stock(daily_sales, period, safety_stock)
    available = calc_available_quantity(stock, incoming)
    return calc_to_order_amount(target, available)


@pytest.mark.parametrize(
    "sku, stock, daily_sales, incoming, lead_days, safety_stock, expected_target, expected_order",
    [
        ("A001", 12, 4, 0, 5, 8, 56, 44),
        ("A002", 50, 3, 20, 4, 10, 43, 0),
        ("A003", 8, 2, 5, 7, 6, 34, 21),
        ("A004", 100, 5, 0, 3, 15, 65, 0),
        ("A005", 0, 0, 0, 2, 0, 0, 0),
        ("A006", 0, 1.5, 0, 1, 2, 14, 14),
    ],
)
def test_sku_from_task(
    sku, stock, daily_sales, incoming, lead_days, safety_stock, expected_target, expected_order
):
    period = calc_coverage_period(lead_days, DAYS_TO_COVER)
    target = calc_target_stock(daily_sales, period, safety_stock)

    assert target == expected_target, sku
    assert calc_order(stock, daily_sales, incoming, lead_days, safety_stock) == expected_order, sku


def test_coverage_period_sums_days():
    assert calc_coverage_period(5, 7) == 12


def test_coverage_period_zero_lead_days():
    assert calc_coverage_period(0, 7) == 7


def test_coverage_period_negative_lead_days():
    with pytest.raises(InvalidInvariant):
        calc_coverage_period(-1, 7)


def test_coverage_period_negative_days_to_cover():
    with pytest.raises(InvalidInvariant):
        calc_coverage_period(5, -1)

@pytest.mark.parametrize(
    "daily_sales, period, safety, expected",
    [
        (10.4, 1, 0, 11),  # round дал бы 10: дробная часть < 0.5
        (0.1, 3, 0, 1),  # 0.3 -> 1
        (2.5, 1, 0, 3),  # банковское round(2.5) == 2
        (3.5, 1, 0, 4),
        (1.5, 8, 2, 14),  # ровно целое (A006)
        (0, 9, 0, 0),  # нулевые продажи
        (0, 9, 5, 5),  # только страховой запас
    ],
)
def test_target_stock_rounds_up(daily_sales, period, safety, expected):
    assert calc_target_stock(daily_sales, period, safety) == expected


def test_target_stock_float_artifact_does_not_add_extra_unit():
    # 1.1 * 10 в float == 11.000000000000002, ceil дал бы 12
    assert calc_target_stock(1.1, 10, 0) == 11


def test_target_stock_negative_daily_sales():
    with pytest.raises(InvalidInvariant):
        calc_target_stock(-0.1, 10, 0)


def test_target_stock_negative_safety_stock():
    with pytest.raises(InvalidInvariant):
        calc_target_stock(1, 10, -1)


def test_target_stock_negative_coverage_period():
    with pytest.raises(InvalidInvariant):
        calc_target_stock(1, -1, 0)


def test_available_quantity_sums_stock_and_incoming():
    assert calc_available_quantity(8, 5) == 13


def test_available_quantity_zeros():
    assert calc_available_quantity(0, 0) == 0


def test_available_quantity_negative_stock():
    with pytest.raises(InvalidInvariant):
        calc_available_quantity(-1, 0)


def test_available_quantity_negative_incoming():
    with pytest.raises(InvalidInvariant):
        calc_available_quantity(0, -1)


def test_to_order_shortage():
    assert calc_to_order_amount(56, 12) == 44


def test_to_order_exact_match_is_zero():
    assert calc_to_order_amount(10, 10) == 0


def test_to_order_surplus_is_zero_not_negative():
    assert calc_to_order_amount(43, 70) == 0


def test_to_order_returns_int():
    assert isinstance(calc_to_order_amount(56, 12), int)


def test_to_order_negative_available():
    with pytest.raises(InvalidInvariant):
        calc_to_order_amount(10, -1)


def test_to_order_negative_target():
    with pytest.raises(InvalidInvariant):
        calc_to_order_amount(-1, 0)


def test_incoming_reduces_order():
    without_incoming = calc_order(8, 2, 0, 7, 6)
    with_incoming = calc_order(8, 2, 5, 7, 6)
    assert without_incoming - with_incoming == 5


def test_order_is_never_negative_with_huge_stock():
    assert calc_order(10_000, 1, 0, 1, 0) == 0


def test_fractional_sales_order_is_integer():
    order = calc_order(0, 0.3, 0, 3, 0)  # 0.3 * 10 = 3.0
    assert order == 3
    assert isinstance(order, int)
