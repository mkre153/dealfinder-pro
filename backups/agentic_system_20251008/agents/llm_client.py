"""
LLM Client for Agent Reasoning
Provides interface to Claude/GPT for intelligent decision-making
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import anthropic


class LLMProvider(Enum):
    """Supported LLM providers"""
    CLAUDE = "claude"
    OPENAI = "openai"


class LLMClient:
    """
    Client for LLM-powered agent reasoning

    Provides structured prompts and response parsing for agent decision-making
    """

    def __init__(self, provider: str = "claude", model: Optional[str] = None):
        """
        Initialize LLM client

        Args:
            provider: LLM provider (claude or openai)
            model: Specific model to use (default: claude-3-5-sonnet-20241022 or gpt-4)
        """
        self.provider = LLMProvider(provider.lower())
        self.logger = logging.getLogger(__name__)

        # Initialize based on provider
        if self.provider == LLMProvider.CLAUDE:
            self.api_key = os.getenv('ANTHROPIC_API_KEY') or os.getenv('CLAUDE_API_KEY')
            self.model = model or "claude-3-5-sonnet-20241022"
            if not self.api_key:
                raise ValueError("ANTHROPIC_API_KEY or CLAUDE_API_KEY not found in environment")
            self.client = anthropic.Anthropic(api_key=self.api_key)

        elif self.provider == LLMProvider.OPENAI:
            import openai
            self.api_key = os.getenv('OPENAI_API_KEY')
            self.model = model or "gpt-4-turbo-preview"
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")
            openai.api_key = self.api_key
            self.client = openai

        self.logger.info(f"LLM Client initialized: {self.provider.value} ({self.model})")

    def generate_response(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        response_format: Optional[str] = None
    ) -> str:
        """
        Generate LLM response

        Args:
            system_prompt: System instruction defining agent role/task
            user_message: User message with context and question
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum response length
            response_format: Optional format (json, text)

        Returns:
            LLM response text
        """
        try:
            if self.provider == LLMProvider.CLAUDE:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_message}
                    ]
                )
                return response.content[0].text

            elif self.provider == LLMProvider.OPENAI:
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]

                if response_format == "json":
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        response_format={"type": "json_object"}
                    )
                else:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )

                return response.choices[0].message.content

        except Exception as e:
            self.logger.error(f"LLM generation failed: {e}", exc_info=True)
            raise

    def generate_structured_response(
        self,
        system_prompt: str,
        user_message: str,
        schema: Dict[str, Any],
        temperature: float = 0.5
    ) -> Dict[str, Any]:
        """
        Generate structured JSON response

        Args:
            system_prompt: System instruction
            user_message: User message
            schema: Expected JSON schema
            temperature: Sampling temperature

        Returns:
            Parsed JSON dict
        """
        # Add JSON formatting instruction
        json_instruction = f"\n\nRespond with ONLY valid JSON matching this schema:\n{json.dumps(schema, indent=2)}"
        enhanced_system = system_prompt + json_instruction

        response_text = self.generate_response(
            system_prompt=enhanced_system,
            user_message=user_message,
            temperature=temperature,
            response_format="json"
        )

        # Parse and validate JSON
        try:
            parsed = json.loads(response_text)
            return parsed
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response: {response_text}")
            # Try to extract JSON from markdown code blocks
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                json_text = response_text[start:end].strip()
                try:
                    return json.loads(json_text)
                except:
                    pass
            raise ValueError(f"Invalid JSON response: {e}")

    def make_decision(
        self,
        context: Dict[str, Any],
        question: str,
        options: List[str],
        agent_role: str
    ) -> Dict[str, Any]:
        """
        Agent decision-making helper

        Args:
            context: Current context/state
            question: Decision question
            options: List of possible decisions
            agent_role: Agent's role/identity

        Returns:
            Dict with 'decision', 'reasoning', 'confidence'
        """
        schema = {
            "decision": "string (one of the provided options)",
            "reasoning": "string (explanation of why this decision)",
            "confidence": "number (0-1, confidence in decision)",
            "considerations": "array of strings (key factors considered)"
        }

        system_prompt = f"""You are an {agent_role} agent for a real estate investment platform.
Your role is to make intelligent, data-driven decisions that maximize ROI and client satisfaction.
Always consider both short-term gains and long-term strategy."""

        user_message = f"""Context:
{json.dumps(context, indent=2)}

Question: {question}

Available Options:
{chr(10).join(f'- {opt}' for opt in options)}

Make the best decision based on the context and your expertise."""

        return self.generate_structured_response(
            system_prompt=system_prompt,
            user_message=user_message,
            schema=schema,
            temperature=0.3  # Lower temp for more consistent decisions
        )

    def analyze_data(
        self,
        data: Dict[str, Any],
        analysis_goal: str,
        agent_role: str
    ) -> Dict[str, Any]:
        """
        Data analysis helper

        Args:
            data: Data to analyze
            analysis_goal: What insights to extract
            agent_role: Agent's role/identity

        Returns:
            Dict with 'insights', 'patterns', 'recommendations'
        """
        schema = {
            "insights": "array of strings (key insights discovered)",
            "patterns": "array of strings (patterns identified in data)",
            "recommendations": "array of strings (actionable recommendations)",
            "confidence": "number (0-1, confidence in analysis)"
        }

        system_prompt = f"""You are an {agent_role} agent specialized in real estate data analysis.
You identify patterns, trends, and actionable insights from property and market data."""

        user_message = f"""Analyze this data:
{json.dumps(data, indent=2)}

Analysis Goal: {analysis_goal}

Provide deep insights and actionable recommendations."""

        return self.generate_structured_response(
            system_prompt=system_prompt,
            user_message=user_message,
            schema=schema
        )

    def generate_message(
        self,
        recipient_context: Dict[str, Any],
        message_goal: str,
        tone: str = "professional"
    ) -> str:
        """
        Generate personalized message

        Args:
            recipient_context: Info about recipient (buyer, seller, etc.)
            message_goal: Purpose of message
            tone: Message tone (professional, friendly, urgent)

        Returns:
            Generated message text
        """
        system_prompt = f"""You are a communication expert for a real estate platform.
You write {tone} messages that are personalized, compelling, and drive action.
Always include specific property details and clear next steps."""

        user_message = f"""Recipient Context:
{json.dumps(recipient_context, indent=2)}

Message Goal: {message_goal}

Generate a concise, compelling message (max 200 words)."""

        return self.generate_response(
            system_prompt=system_prompt,
            user_message=user_message,
            temperature=0.8  # Higher temp for more creative messaging
        )
