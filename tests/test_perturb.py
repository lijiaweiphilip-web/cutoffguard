from cutoffguard import future_perturbation_test


def causal(values, cut):
    return [sum(values[: i + 1]) / (i + 1) for i in range(cut + 1)]


def leaky(values, cut):
    m = sum(values) / len(values)
    return [values[i] - m for i in range(cut + 1)]


def test_causal_stable():
    assert future_perturbation_test([1, 2, 3, 4, 5], 2, causal).stable


def test_leaky_fails():
    assert not future_perturbation_test([1, 2, 3, 4, 5], 2, leaky).stable


def test_bad_index():
    import pytest

    with pytest.raises(ValueError):
        future_perturbation_test([1], 2, causal)
