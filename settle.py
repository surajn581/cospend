import numpy as np
from abc import ABC, abstractmethod
from lib.logging import logger
from settlement_result import SettlementResult

class SettlerBase(ABC):

    def __repr__(self):
        return self.__class__.__name__
 
    @abstractmethod
    def settle(self, inflowNodes: list, outflowNodes: list) -> SettlementResult:
        pass

class OptimialTransactionSettler(SettlerBase):

    @staticmethod
    def _settle( inflowNodes:list, outflowNodes:list ):

        if len(inflowNodes) + len(outflowNodes) == 0:
            return 0, []

        count = float(np.inf)
        transactions = []
        
        outflowNode = outflowNodes[0]
        
        for inflowNode in inflowNodes:
            inflowAmount = abs(inflowNode[1])

            _inflowNodes = inflowNodes[:]
            _outflowNodes = outflowNodes[:]

            _transactions = []

            if inflowAmount == outflowNode[1]:
                _inflowNodes.remove( inflowNode )
                _outflowNodes = _outflowNodes[1:]
                _transactions.append((outflowNode[0], inflowNode[0], inflowAmount))
            elif inflowAmount > outflowNode[1]:            
                _inflowNodes.remove( inflowNode )
                _inflowNodes.append( (inflowNode[0], -(inflowAmount-outflowNode[1])) )
                _outflowNodes = _outflowNodes[1:]
                _transactions.append((outflowNode[0], inflowNode[0], outflowNode[1]))
            else:
                _inflowNodes.remove( inflowNode )
                _outflowNodes = _outflowNodes[1:] + [(outflowNode[0], outflowNode[1]-inflowAmount)]
                _transactions.append((outflowNode[0], inflowNode[0], inflowAmount))
            rcount, rtransactions = OptimialTransactionSettler._settle(_inflowNodes, _outflowNodes)
            if rcount < count:
                count = rcount
                transactions = _transactions + rtransactions
        return count+1, transactions
    
    def settle(self, inflowNodes: list, outflowNodes: list) -> SettlementResult:
        """
        Recursively computes the minimum number of transactions required to settle
        all debts between participants.

        Input:
            inflowNodes (list[tuple[str, float]]): Members owed money (balance < 0).
            outflowNodes (list[tuple[str, float]]): Members who owe money (balance > 0).

        Output:
            SettlementResult

        Notes:
            Uses exhaustive backtracking to guarantee an optimal (minimal) result.
            Complexity is exponential; suitable only for small groups.
        """
        _, transactions = self._settle(inflowNodes=inflowNodes, outflowNodes=outflowNodes)
        return SettlementResult(transactions)
    
class GreedyTransactionSettler(SettlerBase):

    def settle(self, inflowNodes: list, outflowNodes: list) -> SettlementResult:
        """
        Computes a near-optimal settlement of debts using a greedy matching strategy.

        Input:
            inflowNodes: list of (name, balance) where balance < 0  → people who should receive money
            outflowNodes: list of (name, balance) where balance > 0 → people who owe money

        Output:
            SettlementResult
        """
        # Sort by absolute value for deterministic matching
        inflowNodes = sorted(inflowNodes, key=lambda x: x[1])      # most negative first
        outflowNodes = sorted(outflowNodes, key=lambda x: -x[1])   # most positive first

        i = j = 0
        transactions = []

        while i < len(inflowNodes) and j < len(outflowNodes):
            receiver, recv_amt = inflowNodes[i]
            payer, pay_amt = outflowNodes[j]

            amount = min(-recv_amt, pay_amt)
            transactions.append((payer, receiver, round(amount, 2)))

            # Update balances
            inflowNodes[i] = (receiver, recv_amt + amount)
            outflowNodes[j] = (payer, pay_amt - amount)

            # Move pointers if someone is settled
            if abs(inflowNodes[i][1]) < 1e-9:
                i += 1
            if abs(outflowNodes[j][1]) < 1e-9:
                j += 1

        return SettlementResult(transactions)
    
class SmartTransactionSettler(SettlerBase):

    def __init__(self, depth:int=2):
        """
        depth = how many recursive levels to explore (1 = pure greedy)
        """
        self.depth = depth

    def _settle(self, inflowNodes: list, outflowNodes: list, depth:int=2):

        # Base case
        if not inflowNodes or not outflowNodes:
            return 0, []

        # Sort
        inflowNodes = sorted(inflowNodes, key=lambda x: x[1])      # most negative first
        outflowNodes = sorted(outflowNodes, key=lambda x: -x[1])   # most positive first

        best_count = np.inf
        best_transactions = []

        # try top-k matches instead of just one
        K = min(len(inflowNodes), 3)  # try top 3 creditors for each debtor
        for j in range(min(len(outflowNodes), 3)):
            payer, pay_amt = outflowNodes[j]
            for i in range(K):
                receiver, recv_amt = inflowNodes[i]

                amt = min(pay_amt, -recv_amt)

                _inflows = inflowNodes[:]
                _outflows = outflowNodes[:]
                _txns = [(payer, receiver, round(amt, 2))]

                # update balances
                _inflows[i] = (receiver, recv_amt + amt)
                _outflows[j] = (payer, pay_amt - amt)
                _inflows = [x for x in _inflows if abs(x[1]) > 1e-9]
                _outflows = [x for x in _outflows if abs(x[1]) > 1e-9]

                if depth > 1:
                    c, t = self.settle(_inflows, _outflows, depth - 1)
                    count = 1 + c
                    _txns.extend(t)
                else:
                    t = GreedyTransactionSettler().settle(_inflows, _outflows)
                    count = len(t) + 1
                    _txns.extend(t)

                if count < best_count:
                    best_count = count
                    best_transactions = _txns

        return best_count, best_transactions
    
    def settle(self, inflowNodes: list, outflowNodes: list) -> SettlementResult:
        """
        Hybrid approach: limited lookahead recursive matching        
        """
        _, transactions = self._settle(inflowNodes, outflowNodes, self.depth)
        return SettlementResult(transactions)

    
class Settler(SettlerBase):

    def __init__(self, nParticipantsThreshold:int = 8):
        self.nParticipantsThreshold = nParticipantsThreshold

    def __repr__(self):
        return f'{super().__repr__()}(nParticipantsThreshold={self.nParticipantsThreshold})'

    def settle(self, inflowNodes, outflowNodes):
        logger.info(f'Settling with config: {self}')
        nParticipants = len(inflowNodes)+len(outflowNodes)
        if nParticipants<=self.nParticipantsThreshold:
            settleCls = OptimialTransactionSettler
        else:
            settleCls = GreedyTransactionSettler
        logger.info(f'Using {settleCls.__name__} settlement strategy for {nParticipants} participants')
        return settleCls().settle(inflowNodes, outflowNodes)