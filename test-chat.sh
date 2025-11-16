#!/bin/bash
# Test chat with document context

echo "Testing chat with document 3..."
curl -s -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "What is the main contribution of this paper?"}],
    "document_context": [3],
    "use_rag": true,
    "llm_provider": "openai"
  }' | python3 -m json.tool

echo ""
echo "Check LLM service logs for RAG diagnostics:"
docker logs llm-service 2>&1 | grep "/chat" | tail -3
