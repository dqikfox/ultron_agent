import logging
import threading
import time
from web3 import Web3
from .base import Tool

class BlockchainTool(Tool):
    def __init__(self, agent):
        self.name = "blockchain"
        self.description = "Interact with blockchain networks (e.g., Ethereum)."
        self.parameters = {
            "type": "object",
            "properties": {
                "action": {"type": "string", "description": "Action to perform (e.g., get_balance, send_transaction)."},
                "address": {"type": "string", "description": "Blockchain address."},
                "to_address": {"type": "string", "description": "Recipient address for transactions."},
                "amount": {"type": "number", "description": "Amount to send in a transaction."},
                "private_key": {"type": "string", "description": "Private key for signing transactions."}
            },
            "required": ["action"]
        }
        self.agent = agent
        self.config = agent.config
        provider_url = self.config.get('blockchain_provider', 'http://localhost:8545')
        self.web3 = Web3(Web3.HTTPProvider(provider_url))
        self.lock = threading.Lock()
        # self.continuous_blockchain_integration()

    def match(self, user_input: str) -> bool:
        return any(keyword in user_input.lower() for keyword in ["blockchain", "ethereum", "eth", "balance", "transaction"])

    def execute(self, action: str, **kwargs) -> str:
        if not self.web3.is_connected():
            return "Error: Not connected to a blockchain provider. Please check your configuration."

        if action == "get_balance":
            address = kwargs.get("address")
            if not address:
                return "Error: Address is required for get_balance."
            return self._get_balance(address)
        
        elif action == "send_transaction":
            from_address = kwargs.get("address")
            to_address = kwargs.get("to_address")
            amount = kwargs.get("amount")
            private_key = kwargs.get("private_key")
            if not all([from_address, to_address, amount, private_key]):
                return "Error: from_address, to_address, amount, and private_key are required for send_transaction."
            return self._send_transaction(from_address, to_address, amount, private_key)

        return f"Error: Unknown action '{action}'."

    def _get_balance(self, address: str) -> str:
        with self.lock:
            try:
                balance = self.web3.eth.get_balance(address)
                return f"Balance for {address}: {self.web3.from_wei(balance, 'ether')} ETH"
            except Exception as e:
                logging.error(f"Error getting balance: {e} - blockchain_integration.py:59")
                return f"Error getting balance for {address}."

    def _send_transaction(self, from_address: str, to_address: str, amount: float, private_key: str) -> str:
        with self.lock:
            try:
                nonce = self.web3.eth.get_transaction_count(from_address)
                tx = {
                    'nonce': nonce,
                    'to': to_address,
                    'value': self.web3.to_wei(amount, 'ether'),
                    'gas': 21000, # Standard gas limit for a simple ETH transfer
                    'gasPrice': self.web3.eth.gas_price
                }
                signed_tx = self.web3.eth.account.sign_transaction(tx, private_key)
                tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
                return f"Transaction successful. Tx hash: {tx_hash.hex()}"
            except Exception as e:
                logging.error(f"Transaction failed: {e} - blockchain_integration.py:77")
                return f"Transaction failed: {e}"

    def continuous_blockchain_integration(self):
        def blockchain_loop():
            while True:
                # Example continuous task: Monitor contract events or wallet balances
                logging.info("Checking for new blockchain events... - blockchain_integration.py:84")
                time.sleep(600)  # Sleep for 10 minutes

        threading.Thread(target=blockchain_loop, daemon=True).start()

