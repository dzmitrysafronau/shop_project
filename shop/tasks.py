import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def send_order_notification(order_id: int, username: str, total: str):
    """Уведомление о создании заказа"""
    logger.info(f"[ORDER] #{order_id} by {username}, total={total}")
    return True
