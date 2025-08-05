import requests

BASE_URL = "http://localhost:8000/api/v1"

def test_upload():
    pdf_path = "pdf\\Corksy Document - July15.pdf"
    with open(pdf_path, "rb") as file:
        files = {"file": ("Corksy Document - July15.pdf", file, "application/pdf")}
        response = requests.post(f"{BASE_URL}/upload", files=files)
        print("Upload Response:", response.status_code, response.json())

def test_query():
    payload = {"message": "What is the document about?"}
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/query", json=payload, headers=headers)
    print("Query Response:", response.status_code, response.json())

def test_vector_store_status():
    response = requests.get(f"{BASE_URL}/vector-store/status")
    print("Vector Store Status:", response.status_code, response.json())


if __name__ == "__main__":
    # print("=== Test: Upload ===")
    # test_upload()
    print("\n=== Test: Query ===")
    test_query()
    # print("\n=== Test: Vector Store Status ===")
    # test_vector_store_status()