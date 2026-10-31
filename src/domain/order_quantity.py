# Планируем запас на весь срок поставки и ещё на 7 дней. 
# Считаем, что товары, уже находящиеся в пути, поступят не позже новой партии.

from decimal import Decimal
from math import ceil

from src.domain.common import DomainException


class InvalidInvariant(DomainException):
    ...


def calc_coverage_period(lead_days: int, days_to_cover: int) -> int:
    if lead_days < 0:
        raise InvalidInvariant(f"Lead days must be non-negative, but got {lead_days}")

    if days_to_cover < 0:
        raise InvalidInvariant(f"Days to cover must be non-negative, but got {days_to_cover}")

    return lead_days + days_to_cover


def calc_target_stock(daily_sales: Decimal, coverage_period: int, safety_stock: int) -> int:
    if daily_sales < 0:
        raise InvalidInvariant(f"Daily sales must be non-negative, but got {daily_sales}")

    if safety_stock < 0:
        raise InvalidInvariant(f"Safety stock must be non-negative, but got {safety_stock}")

    if coverage_period < 0:
        raise InvalidInvariant(f"Coverage period must be non-negative, but got {coverage_period}")


    return ceil(daily_sales * coverage_period + safety_stock)


def calc_available_quantity(stock: int, incoming: int) -> int:
    if stock < 0:
        raise InvalidInvariant(f"Stock must be non-negative, but got {stock}")

    if incoming < 0:
        raise InvalidInvariant(f"Incoming must be non-negative, but got {incoming}")

    return stock + incoming


def calc_to_order_amount(target_stock: int, available_quantity: int) -> int:
    if available_quantity < 0:
        raise InvalidInvariant(f"Available quantity must be non-negative, but got {available_quantity}")

    if target_stock < 0:
        raise InvalidInvariant(f"Target stock must be non-negative, but got {target_stock}")

    return max(0, target_stock - available_quantity)

