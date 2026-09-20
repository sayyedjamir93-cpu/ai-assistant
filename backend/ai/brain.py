import json
import httpx
from typing import List, Dict, Any, Optional
from backend.config import settings
from backend.ai.prompts import (
    SADIE_SYSTEM_PROMPT,
    STUDY_MODE_PROMPT,
    CODING_MODE_PROMPT
)
from backend.ai.intent import intent_classifier, IntentType, IntentResult


class AIBrain:
    """Core AI layer orchestrating natural language understanding, intent detection, and response generation."""

    def __init__(self):
        self.provider = settings.AI_PROVIDER.lower() if settings.AI_PROVIDER else "gemini"
        self.gemini_key = settings.GEMINI_API_KEY
        self.openai_key = settings.OPENAI_API_KEY
        self.ollama_url = settings.OLLAMA_BASE_URL

    def process_message(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        mode: str = "normal",
        memories: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Process an incoming user message and return intent, response text, and tool execution instructions."""
        history = conversation_history or []
        user_memories = memories or []

        # 1. Detect Intent and extract parameters
        intent_res: IntentResult = intent_classifier.classify_rule_based(user_message)

        # 2. If intent directly requires an immediate tool with a predefined response
        if intent_res.tool_required and intent_res.suggested_response:
            return {
                "intent": intent_res.intent.value,
                "response_text": intent_res.suggested_response,
                "tool_required": True,
                "tool_name": intent_res.tool_name,
                "tool_parameters": intent_res.parameters,
                "mode": mode,
                "source": "intent_engine"
            }

        # 3. Handle Conversational and Knowledge Responses (e.g. "Explain Python recursion")
        # Try external LLM if configured
        llm_response = self._call_external_llm(
            user_message=user_message,
            history=history,
            mode=mode,
            memories=user_memories
        )

        if llm_response:
            return {
                "intent": intent_res.intent.value,
                "response_text": llm_response,
                "tool_required": intent_res.tool_required,
                "tool_name": intent_res.tool_name,
                "tool_parameters": intent_res.parameters,
                "mode": mode,
                "source": self.provider
            }

        # 4. Built-in Offline Knowledge Engine for standard educational & assistant topics
        fallback_text = self._generate_offline_response(user_message, mode=mode, intent=intent_res.intent)

        return {
            "intent": intent_res.intent.value,
            "response_text": fallback_text,
            "tool_required": intent_res.tool_required,
            "tool_name": intent_res.tool_name,
            "tool_parameters": intent_res.parameters,
            "mode": mode,
            "source": "offline_knowledge_engine"
        }

    def _call_external_llm(
        self,
        user_message: str,
        history: List[Dict[str, str]],
        mode: str,
        memories: List[Dict[str, str]]
    ) -> Optional[str]:
        """Attempt to call configured LLM API (Gemini, OpenAI, or Ollama)."""
        # Select system prompt based on mode
        mode_prompt = SADIE_SYSTEM_PROMPT
        if mode == "study":
            mode_prompt += f"\n\n{STUDY_MODE_PROMPT}"
        elif mode == "coding":
            mode_prompt += f"\n\n{CODING_MODE_PROMPT}"

        # Inject memories if present
        if memories:
            memory_block = "\n".join([f"- {m.get('key', '')}: {m.get('value', '')}" for m in memories])
            mode_prompt += f"\n\nKnown user facts from memory:\n{memory_block}"

        # 1. Gemini API
        if self.gemini_key and len(self.gemini_key.strip()) > 5:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
                contents = []
                for h in history[-6:]:
                    role = "user" if h.get("sender") == "user" else "model"
                    contents.append({"role": role, "parts": [{"text": h.get("content", "")}]})
                contents.append({"role": "user", "parts": [{"text": f"{mode_prompt}\n\nUser: {user_message}"}]})

                with httpx.Client(timeout=15.0) as client:
                    resp = client.post(url, json={"contents": contents})
                    if resp.status_code == 200:
                        data = resp.json()
                        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
            except Exception:
                pass

        # 2. OpenAI API
        if self.openai_key and len(self.openai_key.strip()) > 5:
            try:
                url = "https://api.openai.com/v1/chat/completions"
                messages = [{"role": "system", "content": mode_prompt}]
                for h in history[-6:]:
                    role = "user" if h.get("sender") == "user" else "assistant"
                    messages.append({"role": role, "content": h.get("content", "")})
                messages.append({"role": "user", "content": user_message})

                with httpx.Client(timeout=15.0) as client:
                    resp = client.post(
                        url,
                        headers={"Authorization": f"Bearer {self.openai_key}"},
                        json={"model": "gpt-3.5-turbo", "messages": messages, "temperature": 0.7}
                    )
                    if resp.status_code == 200:
                        return resp.json()["choices"][0]["message"]["content"].strip()
            except Exception:
                pass

        # 3. Local Ollama
        if self.ollama_url and self.provider == "ollama":
            try:
                with httpx.Client(timeout=10.0) as client:
                    resp = client.post(
                        f"{self.ollama_url}/api/chat",
                        json={
                            "model": "llama3",
                            "messages": [{"role": "system", "content": mode_prompt}, {"role": "user", "content": user_message}],
                            "stream": False
                        }
                    )
                    if resp.status_code == 200:
                        return resp.json()["message"]["content"].strip()
            except Exception:
                pass

        return None

    def _generate_offline_response(self, text: str, mode: str, intent: IntentType) -> str:
        """Provide intelligent, structured responses offline for common CS topics and queries."""
        lower = text.lower()

        # Recursion query
        if "recursion" in lower:
            return (
                "**Recursion in Programming** is a technique where a function calls itself to solve smaller instances of a problem.\n\n"
                "### Key Components:\n"
                "1. **Base Case**: The stopping condition that prevents infinite recursion.\n"
                "2. **Recursive Step**: The logic where the function reduces the problem and calls itself.\n\n"
                "### Python Example (Factorial):\n"
                "```python\n"
                "def factorial(n):\n"
                "    # Base Case\n"
                "    if n <= 1:\n"
                "        return 1\n"
                "    # Recursive Step\n"
                "    return n * factorial(n - 1)\n\n"
                "print(factorial(5))  # Output: 120\n"
                "```\n\n"
                "💡 *Tip:* Always ensure your base case is reachable, otherwise a `RecursionError: maximum recursion depth exceeded` will occur."
            )

        # Python Error Diagnosis
        if "error" in lower or "bug" in lower or "traceback" in lower:
            return (
                "**Debugging Diagnostic:**\n"
                "To diagnose this error effectively, let's examine:\n"
                "1. **Error Name & Line**: What specific exception was raised (e.g. `IndexError`, `KeyError`, `TypeError`)?\n"
                "2. **Root Cause**: Often caused by uninitialized variables, out-of-bound array indices, or missing null-checks.\n"
                "3. **Resolution**: Add guard clauses, inspect variable states with `print()` or a debugger, and wrap risky blocks in `try...except`."
            )

        # Binary Search / Algorithms
        if "binary search" in lower:
            return (
                "**Binary Search** is an efficient $O(\\log n)$ search algorithm that works on sorted arrays by repeatedly dividing the search interval in half.\n\n"
                "```python\n"
                "def binary_search(arr, target):\n"
                "    low, high = 0, len(arr) - 1\n"
                "    while low <= high:\n"
                "        mid = (low + high) // 2\n"
                "        if arr[mid] == target:\n"
                "            return mid\n"
                "        elif arr[mid] < target:\n"
                "            low = mid + 1\n"
                "        else:\n"
                "            high = mid - 1\n"
                "    return -1\n"
                "```"
            )

        # General greetings / identity
        if any(w in lower for w in ["who are you", "what is your name", "what can you do"]):
            return (
                "I am **SADIE** (*Speech & AI Desktop Intelligent Entity*), your voice-enabled AI personal assistant. "
                "I help you manage study sessions, write and debug code, control safe desktop tools, track tasks, and record notes."
            )

        if any(w in lower for w in ["hello", "hi sadie", "hey sadie", "good morning", "good evening"]):
            return "Hello! I am SADIE, your AI assistant. How can I help you with your studies, tasks, or coding today?"

        return f"I understand you're asking about '{text}'. As Sadie, I'm here to assist you with tasks, study mode, coding assistance, and desktop tools."


brain = AIBrain()
