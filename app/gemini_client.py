import asyncio
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
import google.genai as genai
from google.genai import types as genai_types

from .knowledge_base import get_full_knowledge_base, get_relevant_context

# Load environment variables, temporarily here for SDK client setup.  The main server file also loads the .env;
load_dotenv(Path(__file__).resolve().parent / ".env")

# Logger 
log = logging.getLogger("skedulelt.gemini")

# SDK client (module-level singleton)
_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", ""))
MODEL   = "gemma-3-27b-it"

# Retry constants 
MAX_RETRIES   = 4
BASE_DELAY_S  = 2          # seconds; doubles each attempt

# Thread pool for offloading the blocking SDK call 
_executor = ThreadPoolExecutor(max_workers=4)


# ── Rate-limit queue ─────────────────────────────────────────────────────────
# One asyncio.Queue; a single background worker pulls jobs one at a time.
# Each job is an already-built list of Content objects; the worker calls
# the SDK and puts the result (or exception) into a Future the caller awaits.

_queue: asyncio.Queue | None = None
_worker_task: asyncio.Task  | None = None


def _get_queue() -> asyncio.Queue:
    """Lazily create the queue on the running event loop."""
    global _queue
    if _queue is None:
        _queue = asyncio.Queue()
    return _queue


async def _ensure_worker():
    """Start the single consumer coroutine if it isn't running yet."""
    global _worker_task
    if _worker_task is None or _worker_task.done():
        _worker_task = asyncio.ensure_future(_queue_worker())


async def _queue_worker():
    """
    Pulls (future, contents) tuples from the queue one at a time.
    Calls the Gemini SDK inside a thread, retries on 429, then sets
    the result (or exception) on the future so the caller unblocks.
    """
    q = _get_queue()
    loop = asyncio.get_event_loop()

    while True:
        future, contents = await q.get()
        try:
            answer = await _call_with_retry(loop, contents)
            future.set_result(answer)
        except Exception as exc:
            future.set_exception(exc)
        finally:
            q.task_done()


async def _call_with_retry(loop: asyncio.AbstractEventLoop, contents: list) -> str:
    """
    Synchronous SDK call wrapped in a thread, with exponential back-off
    on 429 responses.
    """
    last_err: Exception | None = None

    for attempt in range(MAX_RETRIES + 1):
        try:
            # Push the blocking network call into the thread pool
            response = await loop.run_in_executor(
                _executor,
                lambda: _client.models.generate_content(
                    model=MODEL,
                    contents=contents,
                ),
            )
            return response.text

        except Exception as exc:
            last_err = exc
            # google-genai raises google.api_core.exceptions.TooManyRequests (429)
            # which has a .code attribute, or we check the string repr.
            status = getattr(exc, "code", None) or getattr(exc, "status_code", None)
            if status == 429 and attempt < MAX_RETRIES:
                delay = BASE_DELAY_S * (2 ** attempt)
                log.warning(
                    "[Queue] 429 — retry %d/%d in %d s", attempt + 1, MAX_RETRIES, delay
                )
                await asyncio.sleep(delay)
            else:
                raise

    raise last_err  # pragma: no cover — loop always raises before here


# System prompt builder

def _build_system_prompt() -> str:
    return (
        "You are the official Skedulelt Support Assistant.\n"
        "Skedulelt is a mobile scheduling & payment app for service providers\n"
        "and customers in Trinidad & Tobago.\n"
        "\n"
        "Rules:\n"
        "  • Answer ONLY based on the knowledge base below.\n"
        "  • If the question falls outside the knowledge base, say:\n"
        '    "I\'m sorry, I don\'t have information on that. Please contact\n'
        '     our support team for further assistance."\n'
        "  • Be friendly, concise, and helpful.\n"
        "  • Do NOT hallucinate features, policies, or prices.\n"
        "  • Respond in English.\n"
        "\n"
        "════════════════════════════════════════════════\n"
        " SKEDULELT KNOWLEDGE BASE\n"
        "════════════════════════════════════════════════\n"
        + get_full_knowledge_base()
        + "\n════════════════════════════════════════════════"
    )


# Public API: Function to chat with Gemini

@dataclass
class ChatResult:
    answer:           str
    matched_sections: list[str]


async def chat(history: list[dict], current_message: str) -> ChatResult:
    """
    Stateless chat.

    Parameters
    ----------
    history : list of {"role": "user"|"assistant", "text": str}
        Full conversation so far — sent by the frontend each time.
    current_message : str
        The user's latest message (not yet in history).

    Returns
    -------
    ChatResult with the model's answer and the keyword-matched section titles.
    """
    # Observability badge data
    ctx = get_relevant_context(current_message)

    # ── Build the contents list Gemini expects ──────────────────────────────
    # [0] user   → system prompt + KB
    # [1] model  → grounding ack
    # [2..n]     → prior turns from frontend
    # [n+1]      → current user message
    contents: list[genai_types.Content] = [
        genai_types.Content(
            role="user",
            parts=[genai_types.Part(text=_build_system_prompt())],
        ),
        genai_types.Content(
            role="model",
            parts=[genai_types.Part(
                text=(
                    "Got it. I'm the Skedulelt Support Assistant. "
                    "I'll answer only based on the knowledge base provided. "
                    "How can I help?"
                )
            )],
        ),
    ]

    for turn in history:
        role = "model" if turn["role"] == "assistant" else "user"
        contents.append(
            genai_types.Content(role=role, parts=[genai_types.Part(text=turn["text"])])
        )

    # Append the current message as the final user turn
    contents.append(
        genai_types.Content(role="user", parts=[genai_types.Part(text=current_message)])
    )

 # Enqueue and await
    q      = _get_queue()
    await  _ensure_worker()

    loop   = asyncio.get_event_loop()
    future = loop.create_future()
    await q.put((future, contents))

    answer = await future

    return ChatResult(answer=answer, matched_sections=ctx.matched)