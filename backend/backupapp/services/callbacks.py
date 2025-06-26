# app/services/callbacks.py

from langchain.callbacks.base import AsyncCallbackHandler
import asyncio

class FastAPIStreamingCallbackHandler(AsyncCallbackHandler):
    def __init__(self):
        self.queue = asyncio.Queue()

    async def on_llm_new_token(self, token: str, **kwargs):
        print("📤 Token:", token)  # ✅ Add this line to log streamed token
        await self.queue.put(token)

    async def on_llm_end(self, *args, **kwargs):
        await self.queue.put(None)
