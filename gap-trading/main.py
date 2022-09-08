from AlgorithmImports import *


class Gaptrading(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2013, 10, 7)  # Set Start Date
        self.SetEndDate(2022, 9, 2)  # Set End Date
        self.SetCash(100000)  # Set Strategy Cash
        self.AddEquity("SPY", Resolution.Daily)

    def OnData(self, data):
        """OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
            Arguments:
                data: Slice object keyed by symbol containing the stock data
        """
        if not self.Portfolio.Invested:
            self.SetHoldings("SPY", 1)
            self.Debug("Purchased Stock")
