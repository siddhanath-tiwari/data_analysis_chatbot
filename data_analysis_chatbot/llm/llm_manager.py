"""
LLM client and operations.
"""
import os
from typing import Dict, Any, List, Optional
from loguru import logger

from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, SystemMessage, AIMessage


class LLMManager:
    """
    Manager for LLM operations.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the LLM manager.
        
        Args:
            config: LLM configuration
        """
        self.config = config
        self.provider = config.get("provider", "openai").lower()
        self.model_name = config.get("model_name", "gpt-3.5-turbo")
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 2000)
        
        self.llm = self._init_llm()
        logger.info(f"LLM initialized: {self.provider} - {self.model_name}")
    
    def _init_llm(self):
        """
        Initialize the LLM based on the configuration.
        
        Returns:
            LLM instance
        """
        if self.provider == "openai":
            api_key = self.config.get("api_key") or os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key not provided")
            
            if "gpt" in self.model_name.lower() or "turbo" in self.model_name.lower():
                return ChatOpenAI(
                    model_name=self.model_name,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    openai_api_key=api_key,
                )
            else:
                return OpenAI(
                    model_name=self.model_name,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    openai_api_key=api_key,
                )
        elif self.provider == "anthropic":
            from langchain.llms import Anthropic
            
            api_key = self.config.get("api_key") or os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("Anthropic API key not provided")
            
            return Anthropic(
                model=self.model_name,
                temperature=self.temperature,
                max_tokens_to_sample=self.max_tokens,
                anthropic_api_key=api_key,
            )
        elif self.provider == "huggingface":
            from langchain.llms import HuggingFaceHub
            
            api_key = self.config.get("api_key") or os.environ.get("HUGGINGFACEHUB_API_TOKEN")
            if not api_key:
                raise ValueError("HuggingFace API key not provided")
            
            return HuggingFaceHub(
                repo_id=self.model_name,
                huggingfacehub_api_token=api_key,
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    def generate(self, prompt: str) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: Prompt text
            
        Returns:
            Generated response
        """
        try:
            response = self.llm(prompt)
            return response
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return f"Error generating response: {str(e)}"
    
    def generate_with_chat_history(
        self, system_message: str, messages: List[Dict[str, str]]
    ) -> str:
        """
        Generate a response with chat history.
        
        Args:
            system_message: System message
            messages: List of message dicts with role and content keys
            
        Returns:
            Generated response
        """
        if self.provider != "openai" or "gpt" not in self.model_name.lower():
            # For non-chat models, concatenate the history
            full_prompt = f"{system_message}\n\n"
            for msg in messages:
                if msg["role"] == "user":
                    full_prompt += f"User: {msg['content']}\n"
                else:
                    full_prompt += f"Assistant: {msg['content']}\n"
            full_prompt += "Assistant: "
            
            return self.generate(full_prompt)
        
        try:
            # Convert messages to langchain format
            langchain_messages = [SystemMessage(content=system_message)]
            
            for msg in messages:
                if msg["role"] == "user":
                    langchain_messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    langchain_messages.append(AIMessage(content=msg["content"]))
            
            response = self.llm(langchain_messages)
            return response.content
        except Exception as e:
            logger.error(f"Error generating chat response: {e}")
            return f"Error generating response: {str(e)}"
    
    def generate_from_template(
        self, template: str, input_variables: Dict[str, Any]
    ) -> str:
        """
        Generate a response using a prompt template.
        
        Args:
            template: Prompt template string
            input_variables: Variables to substitute in the template
            
        Returns:
            Generated response
        """
        try:
            prompt_template = PromptTemplate(
                template=template,
                input_variables=list(input_variables.keys()),
            )
            
            chain = LLMChain(llm=self.llm, prompt=prompt_template)
            response = chain.run(**input_variables)
            
            return response
        except Exception as e:
            logger.error(f"Error generating response from template: {e}")
            return f"Error generating response: {str(e)}"