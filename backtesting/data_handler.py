# backtesting/data_handler.py

import pandas as pd

class DataHandler:
    def __init__(self, data):
        # Your implementation
        if data is None:
            raise ValueError("No dataset detected.")
        if data.empty:
            raise ValueError("Empty dataset detected.")
        self.data = data
        
    def get_data_up_to(self, date):
        date = pd.Timestamp(date)
        if date < self.data.index.min():
            raise ValueError(f"Date {date} is before data starts at {self.data.index.min()}")
        if date > self.data.index.max():
            raise ValueError(f"Date {date} is after data ends at {self.data.index.max()}")
        return self.data[self.data.index <= date]
