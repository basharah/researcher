import api from './api';

export interface Document {
  id: number;
  filename: string;
  upload_date: string;
  file_size?: number;
  page_count?: number;
  title?: string;
  authors?: string;
  abstract?: string;
}

export interface SearchResult {
  chunk_id: number;
  document_id: number;
  document_filename: string;
  section: string;
  text: string;
  similarity_score: number;
}

export interface AnalysisResult {
  document_id: number;
  analysis_type: string;
  result: string;
  timestamp: string;
}

const documentsService = {
  async uploadDocument(file: File): Promise<Document> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  async getDocuments(): Promise<Document[]> {
    const response = await api.get('/documents');
    return response.data.documents || [];
  },

  async getDocument(id: number): Promise<Document> {
    const response = await api.get(`/documents/${id}`);
    return response.data;
  },

  async searchDocuments(query: string, maxResults: number = 10): Promise<SearchResult[]> {
    const response = await api.post('/search', {
      query,
      max_results: maxResults,
    });
    return response.data.results || [];
  },

  async analyzeDocument(
    documentId: number,
    analysisType: 'summary' | 'methodology' | 'findings' | 'gaps' | 'citations'
  ): Promise<AnalysisResult> {
    const response = await api.post('/analyze', {
      document_id: documentId,
      analysis_type: analysisType,
    });
    return response.data;
  },

  async askQuestion(documentId: number, question: string): Promise<{ answer: string }> {
    const response = await api.post('/question', {
      document_id: documentId,
      question,
    });
    return response.data;
  },

  async compareDocuments(documentIds: number[]): Promise<{ comparison: string }> {
    const response = await api.post('/compare', {
      document_ids: documentIds,
    });
    return response.data;
  },
};

export default documentsService;
