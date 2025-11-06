"""
LLM Client - Handles interactions with OpenAI and Anthropic
"""
import openai  # type: ignore
from anthropic import Anthropic  # type: ignore
from typing import List, Dict, Optional, Tuple
import logging
from config import settings
from schemas import LLMProvider

logger = logging.getLogger(__name__)


class LLMClient:
    """Unified client for multiple LLM providers"""
    
    def __init__(self):
        """Initialize LLM clients"""
        self.openai_available = False
        self.anthropic_available = False
        
        # Initialize OpenAI
        if settings.openai_api_key:
            openai.api_key = settings.openai_api_key
            self.openai_available = True
            logger.info("OpenAI client initialized")
        else:
            logger.warning("OpenAI API key not provided")
        
        # Initialize Anthropic
        if settings.anthropic_api_key:
            self.anthropic_client = Anthropic(api_key=settings.anthropic_api_key)
            self.anthropic_available = True
            logger.info("Anthropic client initialized")
        else:
            logger.warning("Anthropic API key not provided")
    
    async def generate(
        self,
        messages: List[Dict[str, str]],
        provider: Optional[LLMProvider] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Tuple[str, str, Optional[int]]:
        """
        Generate response from LLM
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            provider: LLM provider to use
            model: Specific model to use
            max_tokens: Maximum tokens in response
            temperature: Generation temperature
            
        Returns:
            Tuple of (response_text, model_used, tokens_used)
        """
        # Set defaults
        provider = provider or LLMProvider(settings.default_llm_provider)
        temperature = temperature if temperature is not None else settings.temperature
        max_tokens = max_tokens or settings.max_tokens
        
        # Route to appropriate provider
        if provider == LLMProvider.OPENAI:
            return await self._generate_openai(messages, model, max_tokens, temperature)
        elif provider == LLMProvider.ANTHROPIC:
            return await self._generate_anthropic(messages, model, max_tokens, temperature)
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    async def _generate_openai(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str],
        max_tokens: int,
        temperature: float
    ) -> Tuple[str, str, Optional[int]]:
        """Generate response using OpenAI"""
        if not self.openai_available:
            raise ValueError("OpenAI API key not configured")
        
        model = model or settings.default_model
        
        try:
            response = openai.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            text = response.choices[0].message.content
            tokens = response.usage.total_tokens if response.usage else None
            
            logger.info(f"OpenAI response generated: {tokens} tokens, model={model}")
            return text, model, tokens
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def _generate_anthropic(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str],
        max_tokens: int,
        temperature: float
    ) -> Tuple[str, str, Optional[int]]:
        """Generate response using Anthropic Claude"""
        if not self.anthropic_available:
            raise ValueError("Anthropic API key not configured")
        
        model = model or settings.anthropic_model_opus
        
        try:
            # Anthropic uses system/messages format differently
            system_msg = None
            user_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_msg = msg["content"]
                else:
                    user_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            response = self.anthropic_client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_msg,
                messages=user_messages
            )
            
            text = response.content[0].text
            tokens = response.usage.input_tokens + response.usage.output_tokens if response.usage else None
            
            logger.info(f"Anthropic response generated: {tokens} tokens, model={model}")
            return text, model, tokens
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check if any LLM provider is available"""
        return self.openai_available or self.anthropic_available
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        providers = []
        if self.openai_available:
            providers.append("openai")
        if self.anthropic_available:
            providers.append("anthropic")
        return providers


# Singleton instance
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get or create LLM client singleton"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
