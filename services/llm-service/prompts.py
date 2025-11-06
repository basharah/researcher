"""
Prompt Templates for LLM Analysis
"""
from typing import Dict, List
from schemas import AnalysisType


class PromptTemplates:
    """Collection of prompt templates for different analysis types"""
    
    @staticmethod
    def get_system_prompt() -> str:
        """Get the system prompt for research paper analysis"""
        return """You are an expert research assistant specializing in analyzing academic papers. 
Your task is to provide clear, accurate, and insightful analysis of research papers.
Always cite specific sections or findings when making claims.
Be objective and highlight both strengths and limitations."""
    
    @staticmethod
    def get_analysis_prompt(analysis_type: AnalysisType, document_context: str) -> str:
        """
        Get prompt for specific analysis type
        
        Args:
            analysis_type: Type of analysis to perform
            document_context: The document text or relevant sections
            
        Returns:
            Formatted prompt
        """
        prompts = {
            AnalysisType.SUMMARY: f"""Provide a comprehensive summary of the following research paper.
Include:
1. Main research question or objective
2. Methodology used
3. Key findings
4. Conclusions
5. Significance of the work

Document:
{document_context}

Summary:""",

            AnalysisType.LITERATURE_REVIEW: f"""Extract and analyze the literature review from this research paper.
Provide:
1. Main research areas covered
2. Key papers and theories cited
3. Research gaps identified
4. How this work builds on previous research

Document:
{document_context}

Literature Review Analysis:""",

            AnalysisType.KEY_FINDINGS: f"""Identify and explain the key findings from this research paper.
For each finding:
1. State the finding clearly
2. Explain its significance
3. Note any supporting evidence or data
4. Discuss implications

Document:
{document_context}

Key Findings:""",

            AnalysisType.METHODOLOGY: f"""Analyze the methodology section of this research paper.
Discuss:
1. Research design and approach
2. Data collection methods
3. Analysis techniques
4. Strengths of the methodology
5. Potential limitations
6. Reproducibility considerations

Document:
{document_context}

Methodology Analysis:""",

            AnalysisType.RESULTS_ANALYSIS: f"""Analyze the results section of this research paper.
Include:
1. Main results and outcomes
2. Statistical significance (if applicable)
3. How results address the research questions
4. Unexpected findings
5. Relationship to hypotheses

Document:
{document_context}

Results Analysis:""",

            AnalysisType.LIMITATIONS: f"""Identify and discuss the limitations of this research.
Consider:
1. Methodological limitations
2. Data limitations
3. Scope limitations
4. Generalizability concerns
5. Potential biases
6. What the authors acknowledge vs. what else you notice

Document:
{document_context}

Limitations Analysis:""",

            AnalysisType.FUTURE_WORK: f"""Based on this research paper, suggest future research directions.
Discuss:
1. Direct extensions of this work
2. Research gaps that remain
3. New questions raised
4. Methodological improvements
5. Applications to other domains

Document:
{document_context}

Future Research Directions:"""
        }
        
        return prompts.get(analysis_type, document_context)
    
    @staticmethod
    def get_question_prompt(question: str, context_chunks: List[str]) -> str:
        """
        Get prompt for question answering with RAG
        
        Args:
            question: User's question
            context_chunks: Relevant text chunks from vector search
            
        Returns:
            Formatted prompt
        """
        context = "\n\n".join([f"[Source {i+1}]:\n{chunk}" for i, chunk in enumerate(context_chunks)])
        
        return f"""Answer the following question based on the provided research paper excerpts.
Be specific and cite which source(s) support your answer.
If the answer is not in the provided context, say so.

Context from research papers:
{context}

Question: {question}

Answer:"""
    
    @staticmethod
    def get_comparison_prompt(documents_data: List[Dict[str, str]], aspects: List[str] = None) -> str:
        """
        Get prompt for comparing multiple documents
        
        Args:
            documents_data: List of dicts with document info (title, abstract, etc.)
            aspects: Specific aspects to compare
            
        Returns:
            Formatted prompt
        """
        docs_text = "\n\n".join([
            f"Paper {i+1}: {doc.get('title', 'Untitled')}\n{doc.get('abstract', doc.get('text', ''))}"
            for i, doc in enumerate(documents_data)
        ])
        
        if aspects:
            aspects_text = "\n".join([f"- {aspect}" for aspect in aspects])
            comparison_focus = f"\n\nFocus your comparison on these aspects:\n{aspects_text}"
        else:
            comparison_focus = ""
        
        return f"""Compare and contrast the following research papers.
Discuss:
1. Research objectives and questions
2. Methodological approaches
3. Key findings
4. Similarities and differences
5. Complementary or contradictory results
6. Relative strengths and limitations{comparison_focus}

Papers to compare:
{docs_text}

Comparative Analysis:"""
    
    @staticmethod
    def get_chat_prompt_with_context(context_chunks: List[str]) -> str:
        """
        Get system prompt for chat with document context
        
        Args:
            context_chunks: Relevant text chunks from documents
            
        Returns:
            System prompt with context
        """
        context = "\n\n".join([f"[Context {i+1}]:\n{chunk}" for i, chunk in enumerate(context_chunks)])
        
        return f"""You are a helpful research assistant. Use the following context from research papers to answer questions.
When answering:
- Cite specific sources when making claims
- Acknowledge if information is not in the provided context
- Be concise but thorough
- Maintain academic accuracy

Available Context:
{context}"""


prompt_templates = PromptTemplates()
