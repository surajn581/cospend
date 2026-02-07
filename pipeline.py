from lib.logging import logger
from transaction_parser import TransactionInputParser, StringTransactionInputParser
from settlement_result import SettlementResult
import settle

class SettlementPipeline:

    def __init__(self,
                 inputParser: TransactionInputParser = StringTransactionInputParser,
                 nParticipantsThreshold:int = 8):
        self.inputParser = inputParser
        self.nParticipantsThreshold = nParticipantsThreshold

    def _getSettlementTransactions(self, inputTransactions:str)->SettlementResult:
        inflow, outflow = self.inputParser.parse(inputTransactions)
        return settle.Settler(nParticipantsThreshold=self.nParticipantsThreshold).settle(inflow, outflow)
    
    def getSettlementTransactions(self, inputTransactions):
        result = self._getSettlementTransactions(inputTransactions)
        result.logTransactions()
        return result
        