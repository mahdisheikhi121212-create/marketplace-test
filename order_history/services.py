from .models import OrderHistory


def create_order_history(order, status, description=""):
    return OrderHistory.objects.create(
        order=order,
        status=status,
        description=description,
    )