# api/routes.py
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage, AIMessage
from api.schemas import ChatRequest, ChatResponse
from graph.builder import build_graph
import json
import asyncio
from functools import partial

router = APIRouter()
app    = build_graph()

AGENT_NODES  = {"identify", "applicant", "resident", "support"}
STATE_VALUES = {"unknown", "applicant", "resident", "none", ""}

def extract_reply(messages) -> str:
    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            content = msg.content
            if isinstance(content, list):
                text = " ".join(
                    b.get("text", "") for b in content
                    if isinstance(b, dict) and b.get("type") == "text"
                )
            else:
                text = content
            if text.strip():
                return text
    return ""

# ── Standard endpoint ──────────────────────────────────────
@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    config = {"configurable": {"thread_id": request.thread_id}}
    loop   = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        partial(app.invoke,
                {"messages": [HumanMessage(request.message)]},
                config)
    )
    reply = extract_reply(result["messages"])
    return ChatResponse(reply=reply, thread_id=request.thread_id)

# ── Streaming endpoint ─────────────────────────────────────
@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    config = {"configurable": {"thread_id": request.thread_id}}

    async def generate():
        try:
            queue = asyncio.Queue()
            loop  = asyncio.get_running_loop()

            def run_sync():
                for chunk, metadata in app.stream(
                    {"messages": [HumanMessage(request.message)]},
                    config=config,
                    stream_mode="messages"
                ):
                    node = metadata.get("langgraph_node", "")

                    # Only stream from agent nodes
                    if node not in AGENT_NODES:
                        continue

                    # Must have content
                    if not hasattr(chunk, "content"):
                        continue

                    content = chunk.content

                    if isinstance(content, str):
                        # Skip known state value leaks
                        if content.strip().lower() in STATE_VALUES:
                            continue
                        if content:
                            asyncio.run_coroutine_threadsafe(
                                queue.put(content), loop
                            )

                    elif isinstance(content, list):
                        for block in content:
                            if isinstance(block, dict) and block.get("type") == "text":
                                text = block.get("text", "")
                                if text and text.strip().lower() not in STATE_VALUES:
                                    asyncio.run_coroutine_threadsafe(
                                        queue.put(text), loop
                                    )

                asyncio.run_coroutine_threadsafe(queue.put(None), loop)

            loop.run_in_executor(None, run_sync)

            while True:
                text = await queue.get()
                if text is None:
                    break
                yield f"data: {json.dumps({'text': text})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control":     "no-cache",
            "Connection":        "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )