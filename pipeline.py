from lib.logging import logger
from transaction_parser import TransactionInputParser, StringTransactionInputParser
from settlement_result import SettlementResult
import settle

class SettlementPipeline:

    def __init__(self,
                 inputParserKlass: TransactionInputParser,
                 settlerKalss: settle.SettlerBase,
                 settlerKwargs:dict = {}):
        self.inputParserKlass = inputParserKlass
        self.settlerKalss = settlerKalss
        self.settlerKwargs = settlerKwargs

    def _validate(self, inputString:str):
        self.inputParserKlass.validate(inputString)

    def _getSettlementTransactions(self, inputTransactions:str)->SettlementResult:
        inflow, outflow = self.inputParserKlass.parse(inputTransactions)
        return self.settlerKalss(**self.settlerKwargs).settle(inflow, outflow)
    
    def getSettlementTransactions(self, inputTransactions:str, logTransactions:bool=True):
        self._validate(inputTransactions)
        result = self._getSettlementTransactions(inputTransactions)
        if logTransactions:
            result.logTransactions()
        return result
        