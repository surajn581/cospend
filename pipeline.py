from lib.logging import logger
from transaction_parser import TransactionInputParser
import settle

class SettlementPipeline:

    def __init__(self, inputParser: TransactionInputParser):
        self.inputParser = inputParser

    def _getSettlementTransactions(self, inputTransactions):
        inflow, outflow = self.inputParser.parse(inputTransactions)
        if len(inflow)+len(outflow)<=8:
            settleCls = settle.MininumTranscationSettler
        else:
            settleCls = settle.GreedyTransactionSettler        
        return settleCls.settle(inflow, outflow)
    
    def getSettlementTransactions(self, inputTransactions):
        transactions = self._getSettlementTransactions(inputTransactions)
        for borrower, lender, amount in sorted(transactions, key = lambda row: (row[0], -row[-1]) ):
            logger.info(f'{borrower.capitalize()} has to pay {lender.capitalize()} {amount}')