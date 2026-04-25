from __future__ import annotations

import os
import sys

from sqlalchemy import text

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO_ROOT)

from backend.app.core.database import engine  # noqa: E402


def main() -> None:
    results: list[tuple[str, bool, str]] = []

    conn = engine.connect()
    trans = conn.begin()
    try:
        # 0) Identity
        db = conn.execute(text("select current_database()")).scalar_one()
        user = conn.execute(text("select current_user")).scalar_one()
        ver = conn.execute(text("select version()")).scalar_one().splitlines()[0]
        print("CONNECTED_OK")
        print("current_database =", db)
        print("current_user =", user)
        print("version =", ver)

        def probe(name: str, fn) -> None:
            sp = conn.begin_nested()  # SAVEPOINT
            try:
                fn()
                results.append((name, True, "ok"))
                sp.rollback()
            except Exception as e:  # noqa: BLE001 - probe
                results.append((name, True, str(e).splitlines()[0]))
                sp.rollback()

        # 1) users: reject both email+mobile null (should error)
        sp1 = conn.begin_nested()
        try:
            conn.execute(text("INSERT INTO users (name, company_id) VALUES ('X', NULL)"))
            results.append(("users_check_email_or_mobile", False, "unexpectedly inserted"))
        except Exception as e:  # noqa: BLE001
            results.append(("users_check_email_or_mobile", True, str(e).splitlines()[0]))
        finally:
            sp1.rollback()

        # 2) users: unique email when not null (second insert should error)
        sp2 = conn.begin_nested()
        try:
            conn.execute(text("INSERT INTO users (email, name) VALUES ('dup@example.com', 'A')"))
            conn.execute(text("INSERT INTO users (email, name) VALUES ('dup@example.com', 'B')"))
            results.append(("users_unique_email_partial", False, "duplicate email inserted"))
        except Exception as e:  # noqa: BLE001
            results.append(("users_unique_email_partial", True, str(e).splitlines()[0]))
        finally:
            sp2.rollback()

        # 3) users: unique mobile when not null (second insert should error)
        sp3 = conn.begin_nested()
        try:
            conn.execute(text("INSERT INTO users (mobile, name) VALUES ('9999999999', 'A')"))
            conn.execute(text("INSERT INTO users (mobile, name) VALUES ('9999999999', 'B')"))
            results.append(("users_unique_mobile_partial", False, "duplicate mobile inserted"))
        except Exception as e:  # noqa: BLE001
            results.append(("users_unique_mobile_partial", True, str(e).splitlines()[0]))
        finally:
            sp3.rollback()

        # 4) products: unique (company_id, model_number)
        sp4 = conn.begin_nested()
        try:
            cid = conn.execute(
                text(
                    "INSERT INTO companies (name, email, password) "
                    "VALUES ('__tmp_co__', '__tmp_co__@x.com', NULL) RETURNING id"
                )
            ).scalar_one()
            conn.execute(
                text("INSERT INTO products (name, model_number, company_id) VALUES ('P1', 'M-1', :cid)"),
                {"cid": cid},
            )
            conn.execute(
                text("INSERT INTO products (name, model_number, company_id) VALUES ('P2', 'M-1', :cid)"),
                {"cid": cid},
            )
            results.append(("products_unique_company_model", False, "duplicate product inserted"))
        except Exception as e:  # noqa: BLE001
            results.append(("products_unique_company_model", True, str(e).splitlines()[0]))
        finally:
            sp4.rollback()

        print("VALIDATION_PROBES")
        for name, ok, msg in results:
            print(name, "PASS" if ok else "FAIL", "-", msg)

    finally:
        trans.rollback()
        conn.close()


if __name__ == "__main__":
    main()

