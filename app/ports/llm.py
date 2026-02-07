"""LLM port interface.

This module defines the abstract interface for LLM (Large Language Model)
adapters. All LLM implementations must adhere to this contract.
"""

import pydantic
from abc import ABC, abstractmethod


class LLm(ABC):
    """Abstract base class for LLM adapters.

    Defines the contract for synchronous and asynchronous completion methods.
    Implementations should handle their specific API calls and error handling.
    """

    @abstractmethod
    def run_completion(
        self, system_prompt: str, user_prompt: str, dto: type[pydantic.BaseModel]
    ) -> pydantic.BaseModel:
        """Execute a synchronous completion request.

        Args:
            system_prompt: The system's introductory message for the chat.
            user_prompt: The user input for which a response is needed.
            dto: A Pydantic model class defining the structure of the response.

        Returns:
            An instance of the provided DTO class populated with the response data.

        Raises:
            LLMConnectionError: When connection to the LLM service fails.
            LLMRateLimitError: When rate limit is exceeded.
            LLMAuthenticationError: When authentication fails.
            LLMResponseError: When the response is invalid or unexpected.
        """
        pass

    @abstractmethod
    async def run_completion_async(
        self, system_prompt: str, user_prompt: str, dto: type[pydantic.BaseModel]
    ) -> pydantic.BaseModel:
        """Execute an asynchronous completion request.

        Args:
            system_prompt: The system's introductory message for the chat.
            user_prompt: The user input for which a response is needed.
            dto: A Pydantic model class defining the structure of the response.

        Returns:
            An instance of the provided DTO class populated with the response data.

        Raises:
            LLMConnectionError: When connection to the LLM service fails.
            LLMRateLimitError: When rate limit is exceeded.
            LLMAuthenticationError: When authentication fails.
            LLMResponseError: When the response is invalid or unexpected.
        """
        pass
