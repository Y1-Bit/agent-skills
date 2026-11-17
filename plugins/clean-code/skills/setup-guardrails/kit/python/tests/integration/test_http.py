import pytest
from fastapi.testclient import TestClient

from app.entrypoints.http.app import create_app

VALID_BODY = {
    "title": "Dune",
    "short_title": "Dune",
    "isbn": "9780441013593",
    "country_code": "de",
    "genre": "science",
    "librarian_user_id": 1,
}


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


def test_catalog_then_get(client: TestClient) -> None:
    created = client.post("/books", json=VALID_BODY)
    book_id = created.json()["id"]

    fetched = client.get(f"/books/{book_id}")

    assert created.status_code == 201
    assert fetched.json()["country_code"] == "DE"


def test_invalid_value_maps_to_422(client: TestClient) -> None:
    response = client.post("/books", json={**VALID_BODY, "country_code": "DEU"})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_value"


def test_duplicate_maps_to_409(client: TestClient) -> None:
    client.post("/books", json=VALID_BODY)
    assert client.post("/books", json=VALID_BODY).status_code == 409


def test_unknown_book_maps_to_404(client: TestClient) -> None:
    assert client.get("/books/bk_deadbeef").status_code == 404


def test_withdrawing_twice_is_a_rule_violation(client: TestClient) -> None:
    book_id = client.post("/books", json=VALID_BODY).json()["id"]
    client.post(f"/books/{book_id}/withdraw")
    response = client.post(f"/books/{book_id}/withdraw")
    assert response.json()["error"]["code"] == "rule_violation"


def test_request_id_is_propagated(client: TestClient) -> None:
    response = client.get("/books/bk_deadbeef", headers={"X-Request-ID": "req-42"})
    assert response.headers["X-Request-ID"] == "req-42"
