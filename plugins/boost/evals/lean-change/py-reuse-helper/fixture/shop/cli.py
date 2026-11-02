import argparse

from shop.orders import load_orders
from shop.utils import money


def main(argv=None):
    parser = argparse.ArgumentParser(description="Show orders from a CSV export")
    parser.add_argument("path")
    parser.add_argument("--status", help="only orders with this status")
    args = parser.parse_args(argv)

    orders = load_orders(args.path)
    if args.status:
        orders = [o for o in orders if o.status == args.status]

    for o in orders:
        print(f"{o.number}  {o.created}  {o.customer:<20} {money(o.amount):>12}  {o.status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
