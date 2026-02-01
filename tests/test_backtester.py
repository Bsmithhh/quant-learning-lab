# Tests for all backtest components

import pytest
import pandas as pd
from backtesting.data_handler import DataHandler


def test_data_handler_init_rejects_none():
    with pytest.raises(ValueError, match="No dataset"):
        DataHandler(None)


def test_data_handler_init_rejects_empty():
    with pytest.raises(ValueError, match="Empty dataset"):
        DataHandler(pd.DataFrame())


def test_data_handler_get_data_up_to_returns_correct_slice():
    idx = pd.date_range("2023-01-01", periods=5, freq="D")
    df = pd.DataFrame({"Close": [100, 101, 102, 103, 104]}, index=idx)
    h = DataHandler(df)
    out = h.get_data_up_to("2023-01-03")
    assert len(out) == 3
    assert out.index.max() <= pd.Timestamp("2023-01-03")
    pd.testing.assert_frame_equal(out, df.loc[:"2023-01-03"])


def test_data_handler_get_data_up_to_date_before_data_raises():
    idx = pd.date_range("2023-01-01", periods=5, freq="D")
    df = pd.DataFrame({"Close": [100] * 5}, index=idx)
    h = DataHandler(df)
    with pytest.raises(ValueError, match="before data starts"):
        h.get_data_up_to("2022-12-31")


def test_data_handler_get_data_up_to_date_after_data_raises():
    idx = pd.date_range("2023-01-01", periods=5, freq="D")
    df = pd.DataFrame({"Close": [100] * 5}, index=idx)
    h = DataHandler(df)
    with pytest.raises(ValueError, match="after data ends"):
        h.get_data_up_to("2023-06-01")


def test_data_handler_get_data_up_to_last_date_inclusive():
    idx = pd.date_range("2023-01-01", periods=3, freq="D")
    df = pd.DataFrame({"Close": [100, 101, 102]}, index=idx)
    h = DataHandler(df)
    out = h.get_data_up_to("2023-01-03")
    assert len(out) == 3
    assert out.index[-1] == pd.Timestamp("2023-01-03")
