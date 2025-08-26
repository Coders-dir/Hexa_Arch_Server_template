import os
from typing import Any, Dict, List

import httpx


class SupabaseClient:
    def __init__(self, url: str | None = None, key: str | None = None):
        self.url = url or os.getenv("SUPABASE_URL")
        self.key = key or os.getenv("SUPABASE_API_KEY")
        if not self.url or not self.key:
            raise RuntimeError("SUPABASE_URL and SUPABASE_API_KEY must be set")
        self._client = httpx.AsyncClient(base_url=self.url, headers={"apikey": self.key, "Authorization": f"Bearer {self.key}"})

    async def insert(self, table: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        r = await self._client.post(f"/rest/v1/{table}", json=payload)
        r.raise_for_status()
        return r.json()

    async def select(self, table: str, filters: str = "") -> List[Dict[str, Any]]:
        url = f"/rest/v1/{table}"
        if filters:
            url += f"?{filters}"
        r = await self._client.get(url)
        r.raise_for_status()
        return r.json()
