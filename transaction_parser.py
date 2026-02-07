from abc import abstractmethod
import numpy as np
import re
NOT = '!'

class TransactionInputParser:

    @classmethod
    @abstractmethod
    def validate(cls, inputString:str):
        pass
    
    @classmethod
    @abstractmethod
    def parse(cls, allTransactions:str) -> tuple[list, list]:
        pass

class StringTransactionInputParser(TransactionInputParser):

    GROUPKEY = 'group'

    @staticmethod
    def validateChars(allTransactions: str) -> bool:
        """
        Validates that the transaction input string contains only allowed characters.
        allowed characters: alphabets, digits, space, dots, !.

        Args:
            allTransactions (str): Raw input transaction string.

        Raises:
            ValueError: If disallowed characters are found in the input.
        """
        allowed_pattern = re.compile(r'^[a-zA-Z0-9 !\n.]+$')

        if not allowed_pattern.match(allTransactions):
            raise ValueError('invalid chars present in the string')

    @classmethod
    def validate(cls, inputString):
        assert len(inputString)>0, 'Input string cannot be empty'
        cls.validateChars(inputString)
        assert inputString.strip().startswith(cls.GROUPKEY), 'First line must describe the group'
    
    @classmethod
    def parse(cls, allTransactions:str) -> tuple[list, list]:
        """
        Parses a group transaction input string and computes net inflows and outflows 
        for each member.

        Args:
            allTransactions (str): 
                Multiline transaction data in the following format:
                    group <member1> <member2> ...
                    <lender> <amount> <borrower1> <borrower2> ...
                Special rules:
                    - If no borrowers are listed, the amount is split equally among all members.
                    - Borrowers prefixed with '!' are excluded from the split.

        Returns:
            tuple[list[tuple[str, float]], list[tuple[str, float]]]:
                - inflowNodes: Members owed money (balance < 0).
                - outflowNodes: Members who owe money (balance > 0).

        Notes:
            Balances are computed based on equal splits per transaction.
            The method normalizes all names to lowercase for consistency.
        """

        # reading the first line and getting the names of all the group members
        flowMap = {node: 0 for node in allTransactions.lower().strip().split('\n')[0].split(' ')[1:]}

        # iterating over each line starting from the 2nd line
        for transaction in allTransactions.lower().strip().split('\n')[1:]:
            lender, amount, *borrowers = transaction.split(' ')

            # if no borrowers are named then it implies that the amount is to be
            # split equally amongst the whole group
            if not borrowers:
                borrowers = list(flowMap)

            # if borrowers are listed with ! in the beginning of their names then
            # the amount has to be split equally amongst everyone in the group
            # except the names listed with !
            elif NOT in transaction:
                borrowers = list( set(flowMap).difference(set(b[1:] for b in borrowers)) )

            amount = np.round(float(amount)/len(borrowers))
            lenderInflowAmount = 0
            for borrower in borrowers:
                if borrower == lender:
                    continue
                lenderInflowAmount += amount
                flowMap[borrower] += amount
            flowMap[lender] += -lenderInflowAmount

        outflowNodes = {node: value for node, value in flowMap.items() if value>0}
        inflowNodes = {node: value for node, value in flowMap.items() if value<0}

        inflowNodes = list(inflowNodes.items())
        outflowNodes = list(outflowNodes.items())

        return inflowNodes, outflowNodes

