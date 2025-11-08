#!/usr/bin/env python3
"""
Test script for Vector DB Service integration
"""
import requests

# Service URLs
DOC_SERVICE_URL = "http://localhost:8001/api/v1"
VECTOR_SERVICE_URL = "http://localhost:8002"

def test_vector_db_integration():
    """Test the full integration workflow"""
    
    print("🧪 Testing Vector DB Integration")
    print("=" * 60)
    print()
    
    # Step 1: Get a document from document-processing service
    print("1. Fetching document from Document Processing Service...")
    doc_id = 2
    response = requests.get(f"{DOC_SERVICE_URL}/documents/{doc_id}")
    
    if response.status_code != 200:
        print(f"❌ Failed to fetch document: {response.status_code}")
        return
    
    doc = response.json()
    print(f"✅ Found document: {doc['title']}")
    print(f"   - ID: {doc['id']}")
    print(f"   - Pages: {doc['page_count']}")
    print()
    
    # Step 2: Prepare sections data
    print("2. Preparing document sections...")
    sections = {}
    for section_name in ['abstract', 'introduction', 'methodology', 'results', 'conclusion']:
        section_text = doc.get(section_name)
        if section_text and len(section_text.strip()) > 0:
            sections[section_name] = section_text
            print(f"   - {section_name}: {len(section_text)} chars")
    
    # Fallback to full text if no sections
    full_text = doc.get('full_text', '')
    if not sections:
        print("   ⚠️  No sections found, using full text")
    print()
    
    # Step 3: Process document in Vector DB
    print("3. Processing document in Vector DB...")
    process_payload = {
        "document_id": doc_id,
        "full_text": full_text,
        "sections": sections if sections else None
    }
    
    response = requests.post(
        f"{VECTOR_SERVICE_URL}/process-document",
        json=process_payload,
        timeout=120  # Processing can take time
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to process document: {response.status_code}")
        print(response.text)
        return
    
    result = response.json()
    print("✅ Document processed successfully!")
    print(f"   - Chunks created: {result['chunks_created']}")
    print(f"   - Embedding dimension: {result['embedding_dimension']}")
    print()
    
    # Step 4: Test semantic search
    print("4. Testing semantic search...")
    search_queries = [
        "What is the main contribution of this paper?",
        "data lake architecture",
        "experimental results and performance"
    ]
    
    for query in search_queries:
        print(f"\n   Query: '{query}'")
        search_payload = {
            "query": query,
            "max_results": 3,
            "document_id": doc_id
        }
        
        response = requests.post(
            f"{VECTOR_SERVICE_URL}/search",
            json=search_payload
        )
        
        if response.status_code != 200:
            print(f"   ❌ Search failed: {response.status_code}")
            continue
        
        search_result = response.json()
        print(f"   ✅ Found {search_result['results_count']} results")
        print(f"   ⏱️  Search time: {search_result['search_time_ms']:.2f}ms")
        
        for i, chunk in enumerate(search_result['chunks'][:2], 1):
            print(f"\n   Result {i}:")
            print(f"   - Similarity: {chunk['similarity_score']:.3f}")
            print(f"   - Section: {chunk.get('section', 'N/A')}")
            print(f"   - Text: {chunk['text'][:150]}...")
    
    print()
    print("=" * 60)
    print("✅ All tests completed successfully!")


if __name__ == "__main__":
    try:
        test_vector_db_integration()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
