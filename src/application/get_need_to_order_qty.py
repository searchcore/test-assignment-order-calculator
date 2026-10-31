from src.domain.order_quantity import (
    calc_coverage_period, calc_target_stock, calc_available_quantity,
    calc_to_order_amount
)

from src.application.dto import ProductDTO, NeedToOrderDTO


DAYS_TO_COVER = 7


class GetNeedToOrderQty:
    def __call__(self, products: list[ProductDTO]) -> list[NeedToOrderDTO]:
        products_to_order = []

        for p in products:
            to_order = self.process_product(p)

            if to_order.to_order == 0:
                continue

            products_to_order.append(to_order)

        return products_to_order

    def process_product(self, product: ProductDTO) -> NeedToOrderDTO:
        coverage_period = calc_coverage_period(product.lead_days, DAYS_TO_COVER)
        target_stock = calc_target_stock(product.daily_sales, coverage_period, product.safety_stock)
        available_quantity = calc_available_quantity(product.stock, product.incoming)
        to_order = calc_to_order_amount(target_stock, available_quantity)

        return NeedToOrderDTO(
            product.sku,
            to_order,
            target_stock,
            available_quantity,
            product.daily_sales
        )
