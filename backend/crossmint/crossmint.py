import requests
import os
import asyncio
import logging

class Crossmint:
    def __init__(self):
        self.api_key = os.getenv("CROSSMINT_API_KEY")
        self.logger = logging.getLogger(__name__)

    def get_balance(self, user_id):
        url = "https://staging.crossmint.com/api/2025-06-09/wallets/userId:"+user_id+":evm/balances"
        querystring = {"tokens":"usdc","chains":"ethereum-sepolia"}
        headers = {"X-API-KEY": self.api_key}
        response = requests.get(url, params=querystring, headers=headers)
        return response

    async def transfer(self, recipient_address, signer, amount):
        """Async transfer method for Crossmint API"""
        try:
            url = "https://staging.crossmint.com/api/2025-06-09/wallets/userId:"+signer+":evm/tokens/ethereum-sepolia:usdc/transfers"
            payload = {
                "recipient": recipient_address,
                "amount": str(amount),  # Convert to string to avoid Decimal issues
            }
            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }
            
            self.logger.info(f"Making Crossmint transfer: {signer} -> {recipient_address}, amount: {amount}")
            
            # Use asyncio to run the synchronous requests call
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, lambda: requests.post(url, json=payload, headers=headers))
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"Crossmint transfer successful: {result.get('id', 'unknown')}")
                return result
            else:
                self.logger.error(f"Crossmint transfer failed: {response.status_code} - {response.text}")
                return {"error": True, "message": response.text}
                
        except Exception as e:
            self.logger.error(f"Crossmint transfer exception: {str(e)}")
            return {"error": True, "message": str(e)}      
    


