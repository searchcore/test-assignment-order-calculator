import argparse
import csv
import pathlib
from decimal import Decimal

from src.application.dto import ProductDTO, NeedToOrderDTO
from src.application.get_need_to_order_qty import GetNeedToOrderQty



class PresentationException(Exception):
    ...


def read_input_file(filepath: pathlib.Path) -> list[ProductDTO]:
    if filepath.suffix != ".csv":
        raise PresentationException("Bad file extension, only .csv is supported!")

    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)

        if header != ["sku", "name", "stock", "daily_sales", "incoming", "lead_days", "safety_stock"]:
            raise PresentationException("Invalid file format")

        products = []
        for row in reader:
            p = ProductDTO(
                row[0],
                row[1],
                int(row[2]),
                Decimal(row[3]),
                int(row[4]),
                int(row[5]),
                int(row[6]),
            )
            products.append(p)

        return products


def print_to_order(to_order: list[NeedToOrderDTO]):
    print("SKU  | TO ORDER | DESCRIPTION")
    for nto in to_order:
        print(f"{nto.sku:<3} | {nto.to_order:<8} | Целевой запас: {nto.target_stock}, на складе: {nto.available_stock}, продажи в день: {nto.daily_sales:.1f}")


def write_to_file(filepath: pathlib.Path, to_order: list[NeedToOrderDTO]):
    if filepath.suffix != ".csv":
        raise PresentationException("Bad file extension, only .csv is supported!")

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow(["sku", "to_order", "description"])

        for nto in to_order:
            writer.writerow([
                nto.sku,
                nto.to_order,
                f"Целевой запас: {nto.target_stock}, на складе: {nto.available_stock}, продажи в день: {nto.daily_sales}"
            ])


def main():
    parser = argparse.ArgumentParser(description="Рассчет количества товаров для заказа")
    parser.add_argument("--products", required=True, help="CSV файл с товарами, название и порядок колонок: sku, name, stock, daily_sales, incoming, lead_days, safety_stock")
    parser.add_argument("--output-file", type=str, help="Путь к файлу для сохранения результата в CSV")
    parser.add_argument("--print-result", action="store_true", help="Печатать результат в консоль")

    args = parser.parse_args()

    if not (args.print_result or args.output_file):
        print("Ошибка: нужно либо указать файл через --output-file, либо вывод в консоль через --print-result")
        return

    products = read_input_file(pathlib.Path(args.products))

    cmd = GetNeedToOrderQty()
    r = cmd(products)

    if args.output_file:
        out_file = pathlib.Path(args.output_file)

        write_to_file(out_file, r)
        print("Файл сохранен: ", out_file)
        
    if args.print_result:
        print_to_order(r)


if __name__ == "__main__":
    main()
