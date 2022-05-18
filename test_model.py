from datetime import date, timedelta

import pytest

# from model import ...
from app.batch import Batch, AllocateException
from app.order_line import OrderLine

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def make_batch_and_line(sku, batch_qty, line_qty):
    return (
        Batch("batch-001", sku, batch_qty, eta=date.today()),
        OrderLine("order-123", sku, line_qty)
    )


def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch = Batch("batch-001", "SMALL-TABLE", quantity=20, eta=date.today())
    line = OrderLine('order-ref', "SMALL-TABLE", 2)

    batch.allocate(line)

    assert batch.available_quantity == 18


def test_cannot_allocate_if_available_smaller_than_required():
    batch = Batch("batch-001", "SMALL-TABLE", quantity=1, eta=date.today())
    line = OrderLine('order-ref', "SMALL-TABLE", 2)

    with pytest.raises(AllocateException):
        batch.allocate(line)


def test_when_can_allocate_if_available_smaller_than_required_should_return_false():
    small_batch, large_line = make_batch_and_line("ELEGANT-LAMP", 2, 20)

    assert small_batch.can_allocate(large_line) is False


def test_can_allocate_if_available_greater_than_required():
    large_batch, small_line = make_batch_and_line("ELEGANT-LAMP", 20, 2)

    assert large_batch.can_allocate(small_line)


def test_can_allocate_if_available_equal_to_required():
    batch, line = make_batch_and_line("ELEGANT-LAMP", 2, 2)

    assert batch.can_allocate(line)


def test_cannot_allocate_if_skus_do_not_match():
    batch = Batch("batch-001", "UNCOMFORTABLE-CHAIR", 100, eta=None)
    different_sku_line = OrderLine("order-123", "EXPENSIVE-TOASTER", 10)

    assert batch.can_allocate(different_sku_line) is False


def test_can_only_deallocate_allocated_lines():
    batch, unallocated_line = make_batch_and_line("DECORATIVE-TRINKET", 20, 2)
    batch.deallocate(unallocated_line)
    assert batch.available_quantity == 20


def test_can_deallocate_when_order_reference():
    batch, order_line = make_batch_and_line("DECORATIVE-TRINKET", 20, 2)
    batch.allocate(order_line=order_line)

    batch.deallocate(order_line=order_line)

    assert batch.quantity == 20
