from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.core.security import get_current_company
from backend.app.db.base import Base
from backend.app.db.session import get_db
from backend.app.main import app
from backend.app.modules.companies.model import Company
from backend.app.modules.feedback.model import Feedback
from backend.app.modules.products.model import Product
from backend.app.modules.users.model import User


SQLALCHEMY_DATABASE_URL = "sqlite:///./test_customer_analytics.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def _set_auth_company(company_id: int):
    class _CompanyCtx:
        id = company_id

    def _override():
        return _CompanyCtx()

    app.dependency_overrides[get_current_company] = _override


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides = {}
    app.dependency_overrides[get_db] = override_get_db


def teardown_function():
    app.dependency_overrides = {}
    Base.metadata.drop_all(bind=engine)


def test_customer_retention_authenticated_success():
    _set_auth_company(1)
    db = TestingSessionLocal()
    db.add(Company(id=1, name="C1", email="c1@example.com", password="x"))
    db.add(User(id=1, company_id=1, email="u1@example.com", mobile=None, name="U1"))
    db.add(User(id=2, company_id=1, email="u2@example.com", mobile=None, name="U2"))
    db.add(
        Feedback(
            company_id=1,
            user_id=1,
            channel="web",
            text="jan event",
            sentiment="positive",
            sentiment_score=0.9,
            created_at=datetime(2026, 1, 10, tzinfo=timezone.utc),
        )
    )
    db.add(
        Feedback(
            company_id=1,
            user_id=1,
            channel="web",
            text="feb retained",
            sentiment="positive",
            sentiment_score=0.8,
            created_at=datetime(2026, 2, 10, tzinfo=timezone.utc),
        )
    )
    db.add(
        Feedback(
            company_id=1,
            user_id=2,
            channel="web",
            text="feb new",
            sentiment="neutral",
            sentiment_score=0.1,
            created_at=datetime(2026, 2, 11, tzinfo=timezone.utc),
        )
    )
    db.commit()
    db.close()

    client = TestClient(app)
    res = client.get("/analytics/customer-retention")
    assert res.status_code == 200
    payload = res.json()
    assert payload["summary"]["retained_customers"] == 1
    assert payload["summary"]["churned_customers"] == 0
    assert len(payload["retention_over_time"]) == 2


def test_customer_retention_unauthorized():
    client = TestClient(app)
    res = client.get("/analytics/customer-retention")
    assert res.status_code == 401


def test_customer_profile_tenant_isolation():
    db = TestingSessionLocal()
    db.add(Company(id=1, name="C1", email="c1@example.com", password="x"))
    db.add(Company(id=2, name="C2", email="c2@example.com", password="x"))
    db.add(User(id=10, company_id=1, email="user@c1.com", mobile="999", name="U1"))
    db.commit()
    db.close()

    _set_auth_company(2)
    client = TestClient(app)
    res = client.get("/customers/10/profile")
    assert res.status_code == 404


def test_customer_retention_empty_data_case():
    _set_auth_company(1)
    db = TestingSessionLocal()
    db.add(Company(id=1, name="C1", email="c1@example.com", password="x"))
    db.commit()
    db.close()

    client = TestClient(app)
    res = client.get("/analytics/customer-retention")
    assert res.status_code == 200
    payload = res.json()
    assert payload["summary"]["retained_customers"] == 0
    assert payload["summary"]["churned_customers"] == 0
    assert payload["retention_over_time"] == []


def test_customer_profile_authenticated_success():
    _set_auth_company(1)
    db = TestingSessionLocal()
    db.add(Company(id=1, name="C1", email="c1@example.com", password="x"))
    db.add(User(id=11, company_id=1, email="user@c1.com", mobile="9876543210", name="John"))
    db.add(
        Product(
            id=100,
            company_id=1,
            name="Phone",
            description="d",
            model_number="PHONE-1",
        )
    )
    db.add(
        Feedback(
            company_id=1,
            user_id=11,
            product_model_number="PHONE-1",
            channel="web",
            text="good",
            sentiment="positive",
            sentiment_score=0.7,
            created_at=datetime(2026, 3, 1, tzinfo=timezone.utc),
        )
    )
    db.commit()
    db.close()

    client = TestClient(app)
    res = client.get("/customers/11/profile")
    assert res.status_code == 200
    payload = res.json()
    assert payload["id"] == 11
    assert payload["total_feedback_count"] == 1
    assert payload["top_products"][0]["model_number"] == "PHONE-1"
