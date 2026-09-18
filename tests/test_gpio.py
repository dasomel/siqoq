import pytest

from siqoq.gpio import MockGpioAdapter, RealGpioAdapter


def test_mock_gpio_adapter_set_read_round_trip():
    with MockGpioAdapter() as adapter:
        adapter.set_pin(1, True)
        adapter.set_pin(2, False)

        assert adapter.read_pin(1) is True
        assert adapter.read_pin(2) is False


def test_mock_gpio_adapter_default_state_for_unset_pin():
    with MockGpioAdapter() as adapter:
        assert adapter.read_pin(42) is False


def test_mock_gpio_adapter_read_before_open_raises():
    adapter = MockGpioAdapter()

    with pytest.raises(RuntimeError):
        adapter.read_pin(1)


def test_mock_gpio_adapter_set_before_open_raises():
    adapter = MockGpioAdapter()

    with pytest.raises(RuntimeError):
        adapter.set_pin(1, True)


def test_real_gpio_adapter_is_a_documented_stub():
    adapter = RealGpioAdapter()

    with pytest.raises(NotImplementedError):
        adapter.open()
