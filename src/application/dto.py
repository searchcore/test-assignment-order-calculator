from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ProductDTO:
    sku: str
    name: str
    stock: int
    daily_sales: Decimal
    incoming: int
    lead_days: int
    safety_stock: int


@dataclass(frozen=True)
class NeedToOrderDTO:
    sku: str
    to_order: int
    target_stock: int
    available_stock: int
    daily_sales: Decimal
