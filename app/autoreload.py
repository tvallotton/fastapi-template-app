import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(
    prefix="/ws",
)


async def notify_reload(websocket: WebSocket):
    import watchfiles

    async for _ in watchfiles.awatch(".", raise_interrupt=True, rust_timeout=300):
        await websocket.send_text(
            """<div id="ws-notifications"><script>location.reload()</script></div>"""
        )


@router.websocket("/autoreload")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        await asyncio.gather(notify_reload(websocket), websocket.receive_text())
    except WebSocketDisconnect:
        pass
