import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.utils.rabbitmq import RabbitMQClient
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["Notifications"])


active_connections = []


async def process_message_for_websocket(
    message: dict, websocket: WebSocket, is_active: asyncio.Event
):
    """处理 RabbitMQ 消息，并通过 WebSocket 发送给客户端"""
    try:
        if is_active.is_set():
            message_str = json.dumps(message, ensure_ascii=False)
            await websocket.send_text(message_str)
            logger.info(f"Sent message to WebSocket: {message}")
    except Exception as e:
        logger.error(f"Failed to send message to WebSocket: {e}")


@router.websocket("/notification/todo")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    logger.info(f"新的WebSocket连接,当前总数: {len(active_connections)}")

    rabbitmq_client = RabbitMQClient()
    is_active = asyncio.Event()
    is_active.set()

    consumer_task = asyncio.create_task(
        rabbitmq_client.consume_messages(
            queue="todo_notifications",
            callback=lambda msg: process_message_for_websocket(
                msg, websocket, is_active
            ),
        )
    )

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        logger.info("WebSocket 客户端断开连接")
    except Exception as e:
        logger.error(f"WebSocket错误: {e}")
        # 仅在服务器端异常时主动关闭 WebSocket
        await websocket.close()
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)
        is_active.clear()
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            logger.info("RabbitMQ consumer task cancelled")
        await rabbitmq_client.close()
        # 不在这里调用 websocket.close()，依赖框架处理客户端断开
        logger.info(f"WebSocket断开,当前总数: {len(active_connections)}")
