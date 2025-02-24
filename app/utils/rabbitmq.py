import os
import asyncio
import json
from aio_pika import connect_robust, Message, DeliveryMode, IncomingMessage
from aio_pika.abc import AbstractRobustConnection, AbstractChannel
from app.core.logging import get_logger

logger = get_logger(__name__)

# 从环境变量获取RibbitMQ服务器主机名称，默认为 localhost
ribbitmq_host = os.getenv("RIBBITMQ_HOST", "localhost")
RIBBITMQ_URL = f"amqp://user:bitnami@{ribbitmq_host}"

class RabbitMQClient:
    """RabbitMQ 客户端,支持持久化连接,可同时作为Producer和Consumer."""

    _instance = None
    _lock = asyncio.Lock()  # 异步锁，确保单例初始化安全

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.host = RIBBITMQ_URL
        self.connection: AbstractRobustConnection | None = None
        self.channel: AbstractChannel | None = None
        self._initialized = False  # 标记是否已初始化

    async def connect(self):
        """初始化或重连 RabbitMQ"""
        async with self._lock:  # 确保并发初始化安全
            if not self._initialized or not self.connection or self.connection.is_closed:
                self.connection = await connect_robust(self.host)
                self.channel = await self.connection.channel()
                # 可在此声明常用队列
                await self.channel.declare_queue("todo_notifications", durable=True)
                self._initialized = True
                logger.info("RabbitMQ connection established")

    async def send_message(self, message: dict, queue: str):
        """发送消息到指定队列"""
        await self.connect()  # 确保连接可用
        try:
            message_body = json.dumps(message, ensure_ascii=False).encode()  # 防止中文转义
            msg = Message(body=message_body, delivery_mode=DeliveryMode.PERSISTENT)
            await self.channel.default_exchange.publish(msg, routing_key=queue)
            logger.info(f"Sent message to queue '{queue}': {message}")
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise  # 可选择抛出异常让调用者处理

    async def consume_messages(self, queue: str, callback):
        """消费指定队列的消息，并执行回调处理"""
        await self.connect()  # 确保连接可用
        try:
            queue_obj = await self.channel.get_queue(queue)  # 获取现有队列，避免重复声明

            async def on_message(message: IncomingMessage):  
                async with message.process(ignore_processed=True):  # 手动确认模式
                    try:
                        message_body = json.loads(message.body.decode())
                        logger.info(f"Received message from queue '{queue}': {message_body}")
                        await callback(message_body)
                        await message.ack()  # 手动确认
                    except Exception as e:
                        logger.error(f"Failed to process message: {e}")
                        await message.nack(requeue=True)  # 拒绝并重新入队

            await queue_obj.consume(on_message)
            logger.info(f"Started consuming messages from queue: {queue}")
            # 保持消费循环运行
            await asyncio.Future()  # 永久等待，除非任务取消
        except Exception as e:
            logger.error(f"Failed to consume messages: {e}")
            raise

    async def close(self):
        """关闭 RabbitMQ 连接"""
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            self._initialized = False
            logger.info("RabbitMQ connection closed")

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()