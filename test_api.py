import requests

BASE_URL = "http://localhost:8000/api/v1"

def test_upload():
    pdf_path = "pdf\\Corksy Document - July15.pdf"
    with open(pdf_path, "rb") as file:
        files = {"file": ("Corksy Document - July15.pdf", file, "application/pdf")}
        response = requests.post(f"{BASE_URL}/upload", files=files)
        print("Upload Response: ", response.status_code, response.json())

def test_query():
    payload = {"message": "What is the corksy?"}
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/query", json = payload, headers=headers)
    print("Query Response: ", response.status_code, response.json())

def test_vector_store_status():
    response = requests.get(f"{BASE_URL}/vector-store/status")
    print("Vector Store Status: ", response.status_code, response.json())

def test_debug_search():
    query = "What is the wineclub process?"
    response = requests.get(f"{BASE_URL}/debug/search/{query}")
    print("Debug Search Response: ", response.status_code)
    if response.status_code == 200:
        data = response.json()
        print(f"Query: {data['query']}")
        print(f"Vector Store Info: {data['vector_store_info']}")
        print(f"Results Found: {data['results_found']}")
        for result in data['results']:
            print(f"  Rank {result['rank']}: Score = {result['score']:.4f}, Source={result['source_file']}")
            print(f"    Content: {result['content_preview'][: 100]}...")
    else:
        print("Error: ", response.text)

if __name__ == "__main__":
    # print("=== Test: Upload ===")
    # test_upload()
    # print("\n=== Test: Debug Search ===")
    # test_debug_search()
    print("=== Test: Query ===")
    test_query()
    # print("\n=== Test: Vector Store Status ===")
    # test_vector_store_status()
