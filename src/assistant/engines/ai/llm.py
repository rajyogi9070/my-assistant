"""
AI/LLM engine for intelligent responses
"""
import logging
from typing import Optional, Dict, Any
from enum import Enum, auto

from assistant.core.event_bus import EventBus
from assistant.core.config import AIConfig

logger = logging.getLogger(__name__)


class AIProvider(Enum):
    """AI service providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    GOOGLE = "google"


class AIEngine:
    """AI engine for intelligent responses and reasoning"""
    
    def __init__(self, config: AIConfig, event_bus: EventBus):
        self.config = config
        self.event_bus = event_bus
        self.provider = AIProvider(config.provider)
        
        # Initialize client
        self.client = None
        self._init_client()
        
        # Conversation history
        self.conversation_history = []
        
        logger.info(f"AI engine initialized with provider: {self.provider.value}")
    
    def _init_client(self) -> None:
        """Initialize AI client"""
        try:
            if self.provider == AIProvider.OPENAI:
                self._init_openai()
            elif self.provider == AIProvider.ANTHROPIC:
                self._init_anthropic()
            elif self.provider == AIProvider.GOOGLE:
                self._init_google()
            elif self.provider == AIProvider.LOCAL:
                self._init_local()
                
        except Exception as e:
            logger.error(f"Failed to initialize AI client: {e}")
            if self.config.fallback_to_offline:
                logger.info("Falling back to offline mode")
                self.client = None
    
    def _init_openai(self) -> None:
        """Initialize OpenAI client"""
        try:
            from openai import OpenAI
            
            if not self.config.api_key:
                logger.warning("OpenAI API key not configured")
                return
            
            self.client = OpenAI(api_key=self.config.api_key)
            logger.info("OpenAI client initialized")
            
        except ImportError:
            logger.warning("openai package not installed")
    
    def _init_anthropic(self) -> None:
        """Initialize Anthropic client"""
        try:
            import anthropic
            
            if not self.config.api_key:
                logger.warning("Anthropic API key not configured")
                return
            
            self.client = anthropic.Anthropic(api_key=self.config.api_key)
            logger.info("Anthropic client initialized")
            
        except ImportError:
            logger.warning("anthropic package not installed")
    
    def _init_google(self) -> None:
        """Initialize Google Gemini client"""
        try:
            import google.generativeai as genai
            
            if not self.config.api_key:
                logger.warning("Google API key not configured")
                return
            
            genai.configure(api_key=self.config.api_key)
            self.client = genai.GenerativeModel(self.config.model)
            logger.info("Google Gemini client initialized")
            
        except ImportError:
            logger.warning("google-generativeai package not installed")
    
    def _init_local(self) -> None:
        """Initialize local LLM"""
        # Placeholder for local model support
        logger.info("Local LLM mode (not yet implemented)")
        self.client = None
    
    async def chat(self, message: str, context: Dict[str, Any] = None) -> str:
        """Send message to AI and get response"""
        try:
            # Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": message
            })
            
            # Get response based on provider
            if self.provider == AIProvider.OPENAI and self.client:
                response = await self._chat_openai(message, context)
            elif self.provider == AIProvider.ANTHROPIC and self.client:
                response = await self._chat_anthropic(message, context)
            elif self.provider == AIProvider.GOOGLE and self.client:
                response = await self._chat_google(message, context)
            else:
                response = self._chat_offline(message, context)
            
            # Add response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response
            })
            
            # Emit event
            self.event_bus.emit("ai_response", {
                "message": message,
                "response": response,
                "provider": self.provider.value
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error in AI chat: {e}", exc_info=True)
            return "I'm sorry, I encountered an error processing your request."
    
    async def _chat_openai(self, message: str, context: Dict[str, Any] = None) -> str:
        """Chat using OpenAI"""
        try:
            # Prepare messages with system prompt
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant running on a Windows desktop. "
                              "Be concise, friendly, and helpful. Keep responses brief unless "
                              "asked for detailed information."
                }
            ]
            
            # Add recent conversation history (last 10 messages)
            messages.extend(self.conversation_history[-10:])
            
            # Make API call
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI chat error: {e}")
            return self._chat_offline(message, context)
    
    async def _chat_anthropic(self, message: str, context: Dict[str, Any] = None) -> str:
        """Chat using Anthropic Claude"""
        try:
            # Prepare conversation
            messages = self.conversation_history[-10:]
            
            # Make API call
            response = self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                system="You are a helpful AI assistant running on a Windows desktop. "
                      "Be concise, friendly, and helpful.",
                messages=messages
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic chat error: {e}")
            return self._chat_offline(message, context)
    
    async def _chat_google(self, message: str, context: Dict[str, Any] = None) -> str:
        """Chat using Google Gemini"""
        try:
            response = self.client.generate_content(message)
            return response.text
            
        except Exception as e:
            logger.error(f"Google Gemini chat error: {e}")
            return self._chat_offline(message, context)
    
    def _chat_offline(self, message: str, context: Dict[str, Any] = None) -> str:
        """Offline fallback responses"""
        message_lower = message.lower()
        
        # Simple pattern-based responses
        if any(word in message_lower for word in ["hello", "hi", "hey"]):
            return "Hello! How can I help you today?"
        
        elif "how are you" in message_lower:
            return "I'm doing great, thank you for asking! How can I assist you?"
        
        elif "thank" in message_lower:
            return "You're welcome! Is there anything else I can help with?"
        
        elif "bye" in message_lower or "goodbye" in message_lower:
            return "Goodbye! Have a great day!"
        
        elif "time" in message_lower:
            from datetime import datetime
            return f"The current time is {datetime.now().strftime('%I:%M %p')}"
        
        elif "date" in message_lower:
            from datetime import datetime
            return f"Today is {datetime.now().strftime('%B %d, %Y')}"
        
        elif "name" in message_lower:
            return "I'm your AI Assistant. How can I help you?"
        
        else:
            return "I'm not sure how to help with that. Could you rephrase or ask something else?"
    
    def clear_history(self) -> None:
        """Clear conversation history"""
        self.conversation_history.clear()
        logger.info("Conversation history cleared")
    
    def get_history(self) -> list:
        """Get conversation history"""
        return self.conversation_history.copy()
    
    def set_provider(self, provider: str) -> bool:
        """Change AI provider"""
        try:
            self.provider = AIProvider(provider)
            self._init_client()
            logger.info(f"AI provider changed to: {provider}")
            return True
        except Exception as e:
            logger.error(f"Failed to change provider: {e}")
            return False
