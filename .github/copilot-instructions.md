# Research Paper Analysis Chatbot - Microservices Project

## Project Overview
A microservices-based chatbot system for analyzing research papers, extracting literature reviews, and conducting research assistance.

## Architecture
- **Document Processing Service**: PDF upload, text extraction, section parsing
- **Vector Database Service**: Embeddings generation and semantic search
- **LLM Service**: AI-powered analysis using OpenAI/Claude
- **API Gateway**: Service orchestration
- **Frontend**: React-based chat interface

## Technology Stack
- Backend: Python FastAPI
- Database: PostgreSQL with pgvector
- Cache: Redis
- Containerization: Docker
- Frontend: React

## Learning Path
Each service is built incrementally to facilitate learning and understanding of microservices architecture.
