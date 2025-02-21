import pytest
import requests
import logging
from faker import Faker
from jsonschema import validate

BASE_URL = "https://fakerestapi.azurewebsites.net/api/v1/Authors"
faker = Faker()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def valid_create_author_payload(faker):
    return {
        "id": faker.random_int(1000, 9999),
        "idBook": faker.random_int(1, 100),
        "firstName": faker.first_name(),
        "lastName": faker.last_name()
    }

def missing_first_name(faker):
    return {
        "id": faker.random_int(1000, 9999),
        "idBook": faker.random_int(1, 100),
        # firstName is missing
        "lastName": faker.last_name()
    }

def missing_last_name(faker):
    return {
        "id": faker.random_int(1000, 9999),
        "idBook": faker.random_int(1, 100),
        "firstName": faker.first_name(),
        # lastName is missing
    }

def invalid_id_type(faker):
    return {
        "id": "invalid_id",  # wrong type
        "idBook": faker.random_int(1, 100),
        "firstName": faker.first_name(),
        "lastName": faker.last_name()
    }

def extra_field(faker):
    return {
        "id": faker.random_int(1000, 9999),
        "idBook": faker.random_int(1, 100),
        "firstName": faker.first_name(),
        "lastName": faker.last_name(),
        "extraField": "extra_value"  # extra field that the API ignores
    }

def null_first_name(faker):
    return {
        "id": faker.random_int(1000, 9999),
        "idBook": faker.random_int(1, 100),
        "firstName": None,
        "lastName": faker.last_name()
    }

def null_last_name(faker):
    return {
        "id": faker.random_int(1000, 9999),
        "idBook": faker.random_int(1, 100),
        "firstName": faker.first_name(),
        "lastName": None,
    }

def null_id(faker):
    return {
        "id": None,
        "idBook": faker.random_int(1, 100),
        "firstName": faker.first_name(),
        "lastName": faker.last_name(),
    }

def null_book_id(faker):
    return {
        "id": faker.random_int(1000, 9999),
        "idBook": None,
        "firstName": faker.first_name(),
        "lastName": faker.last_name(),
    }

@pytest.mark.parametrize("payload_func, expected_status", [
    (valid_create_author_payload, 200),
    (missing_first_name, 200),
    (missing_last_name, 200),
    (invalid_id_type, 400),
    (extra_field, 200),
    (null_first_name, 200),
    (null_last_name, 200),
    (null_id, 400),
    (null_book_id, 400)
])
def test_create_author(payload_func, expected_status):
    payload = payload_func(faker)
    response = requests.post(BASE_URL, json=payload)
    logging.info(f"Payload: {payload} - Status: {response.status_code} - Response: {response.text}")
    assert response.status_code == expected_status, f"Expected {expected_status} but got {response.status_code}"

    if response.status_code == 200:
        response_data = response.json()

        # When a field is missing in the payload, the API returns null.
        expected_firstName = payload.get("firstName", None)
        expected_lastName = payload.get("lastName", None)

        assert response_data["id"] == payload["id"], "ID mismatch"
        assert response_data["idBook"] == payload["idBook"], "Book ID mismatch"
        assert response_data["firstName"] == expected_firstName, "First name mismatch"
        assert response_data["lastName"] == expected_lastName, "Last name mismatch"

        # Define the expected JSON schema for a successful response.
        schema = {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "idBook": {"type": "integer"},
                "firstName": {"type": ["string", "null"]},
                "lastName": {"type": ["string", "null"]}
            },
            "required": ["id", "idBook", "firstName", "lastName"]
        }
        validate(instance=response_data, schema=schema)

    elif response.status_code == 400:
        error_data = response.json()
        assert error_data["title"] == "One or more validation errors occurred.", "Title value is not correct"
        assert "type" in error_data, "Missing 'type' in error response"
        assert "title" in error_data, "Missing 'title' in error response"
        assert "status" in error_data, "Missing 'status' in error response"
        assert "traceId" in error_data, "Missing 'traceId' in error response"
        assert "errors" in error_data, "Missing 'errors' in error response"
        assert error_data["status"] == expected_status, "Error status does not match expected"

        # Define the expected JSON schema for an error response.
        error_schema = {
            "type": "object",
            "properties": {
                "type": {"type": "string"},
                "title": {"type": "string"},
                "status": {"type": "integer"},
                "traceId": {"type": "string"},
                "errors": {"type": "object"}
            },
            "required": ["type", "title", "status", "traceId", "errors"]
        }
        # Validate schema
        validate(instance=error_data, schema=error_schema)


@pytest.mark.parametrize("payload_func, expected_status", [
    (valid_create_author_payload, 200)
])
def test_author_crud(payload_func, expected_status):
    # Create author
    payload = payload_func(faker)
    create_res = requests.post(BASE_URL, json=payload)
    logging.info(f"Create: {payload} => {create_res.status_code} - {create_res.text}")
    assert create_res.status_code == expected_status, f"Expected {expected_status} but got {create_res.status_code}"
    author_id = create_res.json()["id"]

    list_error = None
    try:
        # Fetch all authors and validate schema.
        get_res = requests.get(BASE_URL)
        assert get_res.status_code == 200, "Fetching authors was not successful"
        authors = get_res.json()
        get_schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "idBook": {"type": "integer"},
                    "firstName": {"type": ["string", "null"]},
                    "lastName": {"type": ["string", "null"]}
                },
                "required": ["id", "idBook", "firstName", "lastName"]
            }
        }
        validate(instance=authors, schema=get_schema)

        # Verify that the created author exists in the list and validate its fields.
        matching_author = next((author for author in authors if author["id"] == author_id), None)
        if not matching_author:
            list_error = AssertionError("Created author not found in list")
            raise list_error

        # Validate rest of the fields
        assert matching_author["idBook"] == payload["idBook"], "idBook mismatch"
        expected_first_name = payload.get("firstName", None)
        expected_last_name = payload.get("lastName", None)
        assert matching_author["firstName"] == expected_first_name, "First name mismatch"
        assert matching_author["lastName"] == expected_last_name, "Last name mismatch"

    finally:
        # delete the created author
        delete_res = requests.delete(f"{BASE_URL}/{author_id}")
        logging.info(f"Delete Author [{author_id}] => {delete_res.status_code} - {delete_res.text}")
        assert delete_res.status_code == 200, f"Expected deletion status 200 but got {delete_res.status_code}"
        assert len(delete_res.content) == 0, "Delete response is not empty"
        assert delete_res.headers.get("Content-Length") in (None, "0"), "Delete response Content-Length is not 0"

        # Verify that the author is no longer present (after deletion)
        get_after = requests.get(BASE_URL)
        assert get_after.status_code == 200, "Fetching authors after deletion was not successful"
        authors_after = get_after.json()
        assert not any(author["id"] == author_id for author in authors_after), "Deleted author still found in list"

    if list_error:
        raise list_error
