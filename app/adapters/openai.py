"""OpenAI adapter implementation.

This module provides the OpenAI implementation of the LLm port interface,
handling API calls and translating OpenAI-specific errors to application errors.
"""

import openai
import pydantic

from app import ports
from app.exceptions import (
    LLMAuthenticationError,
    LLMConnectionError,
    LLMRateLimitError,
    LLMResponseError,
)


class OpenAIAdapter(ports.LLm):
    """OpenAI LLM adapter implementation.

    Implements the LLm port interface using OpenAI's API for both
    synchronous and asynchronous completion requests.
    """

    _model: str
    _client: openai.OpenAI
    _aclient: openai.AsyncOpenAI

    def __init__(self, api_key: str, model: str) -> None:
        """Initialize the OpenAI adapter.

        Args:
            api_key: OpenAI API key for authentication.
            model: Model identifier (e.g., 'gpt-4o-2024-08-06').
        """
        self._model = model
        self._client = openai.OpenAI(api_key=api_key)
        self._aclient = openai.AsyncOpenAI(api_key=api_key)

    def run_completion(
        self, system_prompt: str, user_prompt: str, dto: type[pydantic.BaseModel]
    ) -> pydantic.BaseModel:
        """Execute a synchronous completion request using the OpenAI API.

        Args:
            system_prompt: The system's introductory message for the chat.
            user_prompt: The user input for which a response is needed.
            dto: A Pydantic model class defining the structure of the API response.

        Returns:
            An instance of the provided DTO class populated with the API response data.

        Raises:
            LLMConnectionError: When connection to OpenAI fails.
            LLMRateLimitError: When OpenAI rate limit is exceeded.
            LLMAuthenticationError: When OpenAI authentication fails.
            LLMResponseError: When the response is invalid or unexpected.
        """
        try:
            completion = self._client.beta.chat.completions.parse(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format=dto,
            )
            parsed = completion.choices[0].message.parsed
            if parsed is None:
                raise LLMResponseError(
                    "OpenAI returned empty or unparseable response"
                )
            return parsed
        except openai.AuthenticationError as e:
            raise LLMAuthenticationError(
                "OpenAI authentication failed. Check your API key.", e
            ) from e
        except openai.RateLimitError as e:
            raise LLMRateLimitError(
                "OpenAI rate limit exceeded. Please retry later.", e
            ) from e
        except openai.APIConnectionError as e:
            raise LLMConnectionError(
                "Failed to connect to OpenAI API.", e
            ) from e
        except openai.APIStatusError as e:
            raise LLMResponseError(
                f"OpenAI API error: {e.message}", e
            ) from e

    async def run_completion_async(
        self, system_prompt: str, user_prompt: str, dto: type[pydantic.BaseModel]
    ) -> pydantic.BaseModel:
        """Execute an asynchronous completion request using the OpenAI API.

        Args:
            system_prompt: The system's introductory message for the chat.
            user_prompt: The user input for which a response is needed.
            dto: A Pydantic model class defining the structure of the API response.

        Returns:
            An instance of the provided DTO class populated with the API response data.

        Raises:
            LLMConnectionError: When connection to OpenAI fails.
            LLMRateLimitError: When OpenAI rate limit is exceeded.
            LLMAuthenticationError: When OpenAI authentication fails.
            LLMResponseError: When the response is invalid or unexpected.
        """
        try:
            completion = await self._aclient.beta.chat.completions.parse(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format=dto,
            )
            parsed = completion.choices[0].message.parsed
            if parsed is None:
                raise LLMResponseError(
                    "OpenAI returned empty or unparseable response"
                )
            return parsed
        except openai.AuthenticationError as e:
            raise LLMAuthenticationError(
                "OpenAI authentication failed. Check your API key.", e
            ) from e
        except openai.RateLimitError as e:
            raise LLMRateLimitError(
                "OpenAI rate limit exceeded. Please retry later.", e
            ) from e
        except openai.APIConnectionError as e:
            raise LLMConnectionError(
                "Failed to connect to OpenAI API.", e
            ) from e
        except openai.APIStatusError as e:
            raise LLMResponseError(
                f"OpenAI API error: {e.message}", e
            ) from e
