from market_data_processor import MarketDataProcessor


def test_returns_exist():
    mdp = MarketDataProcessor("AAPL", "2020-01-01", "2020-06-01")
    mdp.fetch_prices()
    mdp.add_returns()
    assert "ret_1d" in mdp.data.columns
