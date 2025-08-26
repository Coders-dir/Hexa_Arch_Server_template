from fastapi import Request, HTTPException
from starlette.types import ASGIApp, Receive, Scope, Send


class DispatcherMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)
        api_key = request.headers.get("x-api-key", "anonymous")

        # get quota manager from app state if available
        qm = getattr(request.app.state, "quota_manager", None)
        if qm is not None:
            allowed = await qm.consume(f"key:{api_key}", window=60, limit=60)
            if not allowed:
                raise HTTPException(status_code=429, detail="rate limit exceeded")

        await self.app(scope, receive, send)
