from lib.logging import logger
from transaction_parser import TransactionInputParser, StringTransactionInputParser
from settlement_result import SettlementResult
import settle

class SettlementPipeline:

    def __init__(self,
                 inputParserKlass: TransactionInputParser = StringTransactionInputParser,
                 nParticipantsThreshold:int = 8):
        self.inputParserKlass = inputParserKlass
        self.nParticipantsThreshold = nParticipantsThreshold

    def _validate(self, inputString:str):
        self.inputParserKlass.validate(inputString)

    def _getSettlementTransactions(self, inputTransactions:str)->SettlementResult:
        inflow, outflow = self.inputParserKlass.parse(inputTransactions)
        return settle.Settler(nParticipantsThreshold=self.nParticipantsThreshold).settle(inflow, outflow)
    
    def getSettlementTransactions(self, inputTransactions:str):
        self._validate(inputTransactions)
        result = self._getSettlementTransactions(inputTransactions)
        result.logTransactions()
        return result
        