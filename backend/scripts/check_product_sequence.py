from __future__ import annotations

import os
import sys

from sqlalchemy import text

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO_ROOT)

from backend.app.core.database import engine  # noqa: E402


def main() -> None:
    with engine.connect() as c:
        max_id = c.execute(text("select coalesce(max(id),0) from products")).scalar_one()
        seq = c.execute(text("select pg_get_serial_sequence('products','id')")).scalar_one()
        print("max_product_id =", max_id)
        print("sequence =", seq)
        if seq:
            last_value, is_called = c.execute(text(f"select last_value, is_called from {seq}")).first()
            print("seq_last_value =", last_value, "is_called =", is_called)


if __name__ == "__main__":
    main()

