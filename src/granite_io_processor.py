"""
Granite-IO Processing Integration

This module provides Granite-IO framework integration for the RCA system,
offering an alternative to BeeAI framework processing with enhanced capabilities.

SPDX-License-Identifier: Apache-2.0
"""

from granite_io import make_backend, make_io_processor
from granite_io.types import ChatCompletionInputs, UserMessage
import asyncio


class GraniteIOProcessor:
    """Granite-IO processing class for AI-powered analysis."""
    
    def __init__(self, model_name="granite3.2:8b", backend_type="openai"):
        """
        Initialize the Granite-IO processor.
        
        Args:
            model_name: Name of the Granite model to use
            backend_type: Backend type (openai, litellm, transformers)
        """
        self.model_name = model_name
        self.backend_type = backend_type
        self._io_processor = None
        self._initialize_processor()
    
    def _initialize_processor(self):
        """Initialize the Granite-IO processor with backend."""
        try:
            backend = make_backend(self.backend_type, {"model_name": self.model_name})
            self._io_processor = make_io_processor(self.model_name, backend=backend)
        except Exception as e:
            raise Exception(f"Failed to initialize Granite-IO processor: {e}")
    
    async def create_chat_completion(self, prompt, use_thinking=False):
        """
        Create a chat completion using Granite-IO framework.
        
        Args:
            prompt: The prompt text to send to the model
            use_thinking: Whether to enable thinking mode
            
        Returns:
            The model's response text
        """
        if not self._io_processor:
            raise Exception("Granite-IO processor not initialized")
        
        try:
            messages = [UserMessage(content=prompt)]
            inputs = ChatCompletionInputs(messages=messages, thinking=use_thinking)
            
            # Use async version if available, otherwise fall back to sync
            if hasattr(self._io_processor, 'acreate_chat_completion'):
                outputs = await self._io_processor.acreate_chat_completion(inputs)
            else:
                # Run sync method in executor to avoid blocking
                loop = asyncio.get_event_loop()
                outputs = await loop.run_in_executor(
                    None, 
                    self._io_processor.create_chat_completion, 
                    inputs
                )
            
            # Extract response content
            if outputs.results and len(outputs.results) > 0:
                result = outputs.results[0]
                if hasattr(result, 'next_message'):
                    if use_thinking and hasattr(result.next_message, 'reasoning_content'):
                        # If thinking is enabled and available, combine reasoning and response
                        reasoning = result.next_message.reasoning_content or ""
                        content = result.next_message.content or ""
                        if reasoning:
                            return f"**Reasoning:**\n{reasoning}\n\n**Response:**\n{content}"
                        else:
                            return content
                    else:
                        return result.next_message.content or str(result)
                else:
                    return str(result)
            else:
                return "No response generated"
                
        except Exception as e:
            raise Exception(f"Failed to create chat completion: {e}")
    
    def get_info(self):
        """Get information about the processor configuration."""
        return {
            "framework": "granite-io",
            "model_name": self.model_name,
            "backend_type": self.backend_type,
            "processor_available": self._io_processor is not None
        }


async def test_granite_io_processor():
    """Test function for Granite-IO processor."""
    try:
        processor = GraniteIOProcessor()
        test_prompt = "Analyze this system error: 'Connection timeout on port 443'"
        
        print("Testing Granite-IO processor...")
        print(f"Processor info: {processor.get_info()}")
        
        response = await processor.create_chat_completion(test_prompt)
        print(f"Response: {response}")
        
        return True
    except Exception as e:
        print(f"Granite-IO processor test failed: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(test_granite_io_processor())
