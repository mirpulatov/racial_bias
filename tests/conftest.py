import pytest
from alembic.config import main
from starlette.config import environ
from starlette.testclient import TestClient


environ["TESTING"] = "TRUE"


@pytest.fixture
def client():
    from web.main import app

    main(["--raiseerr", "upgrade", "head"])

    with TestClient(app=app) as client:
        yield client

    main(["--raiseerr", "downgrade", "base"])
