"""Common interface for all external feed adapters."""
from abc import ABC, abstractmethod
from typing import Any
import httpx
class FeedAdapter(ABC):
    name: str = "base"
    source_label: str = "base"
    @abstractmethod
    async def fetch(self) -> list[dict[str, Any]]:
        """Fetch raw data from the external source."""
        ...
    @abstractmethod
    def normalise(self, raw: Any) -> dict | None:
        """Convert one raw item into the internal incident schema dict."""
        ...
    async def run(self) -> list[dict]:
        """Fetch + normalise, skipping bad items."""
        async with httpx.AsyncClient(timeout=20.0) as client:
            self._client = client
            raw_items = await self.fetch()
        results = []
        for raw in raw_items:
            try:
                norm = self.normalise(raw)
                if norm:
                    results.append(norm)
            except Exception as e:
                print(f"[{self.name}] normalise error: {e}")
        return results
