from lib.logging import logger

class SettlementResult:

    def __init__(self, transactions:tuple):
        self.transactions = transactions

    @property
    def count(self):
        return len(self.transactions)
    
    def __len__(self):
        return self.count
        
    def __iter__(self):
        return iter(self.transactions)

    def logTransactions(self):
        logger.info(f'Number of transactions: {self.count}')
        for borrower, lender, amount in sorted(self.transactions, key = lambda row: (row[0], -row[-1]) ):
            logger.info(f'{borrower.capitalize()} has to pay {lender.capitalize()} {amount}')