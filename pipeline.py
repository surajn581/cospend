from lib.logging import logger
from transaction_parser import TransactionInputParser, StringTransactionInputParser
import settle

class SettlementPipeline:

    def __init__(self,
                 inputParser: TransactionInputParser = StringTransactionInputParser,
                 nParticipantsThreshold:int = 8):
        self.inputParser = inputParser
        self.nParticipantsThreshold = nParticipantsThreshold

    def _getSettlementTransactions(self, inputTransactions):
        inflow, outflow = self.inputParser.parse(inputTransactions)
        return settle.Settler(nParticipantsThreshold=self.nParticipantsThreshold).settle(inflow, outflow)
    
    def getSettlementTransactions(self, inputTransactions):
        transactions = self._getSettlementTransactions(inputTransactions)
        for borrower, lender, amount in sorted(transactions, key = lambda row: (row[0], -row[-1]) ):
            logger.info(f'{borrower.capitalize()} has to pay {lender.capitalize()} {amount}')