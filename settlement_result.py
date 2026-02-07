from lib.logging import logger

class SettlementResult:

    def __init__(self, transactions:tuple):
        self.transactions = transactions

    @property
    def count(self):
        return len(self.transactions)

    def logTransactions(self):
        for borrower, lender, amount in sorted(self.transactions, key = lambda row: (row[0], -row[-1]) ):
            logger.info(f'{borrower.capitalize()} has to pay {lender.capitalize()} {amount}')