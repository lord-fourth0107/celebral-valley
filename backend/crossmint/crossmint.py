import requests
import os
class Crossmint:
    def __init__(self):
        self.api_key = os.getenv("CROSSMINT_API_KEY")

    def get_balance(self,user_id):
        url = "https://staging.crossmint.com/api/2025-06-09/wallets/userId:"+user_id+":evm/balances"
        querystring = {"tokens":"usdc","chains":"ethereum-sepolia"}
        headers = {"X-API-KEY": self.api_key}
        response = requests.get(url, params=querystring, headers=headers)
        return response
    def transfer(self,reciepient_address,signer,amount):

        url = "https://staging.crossmint.com/api/2025-06-09/wallets/userId:"+signer+":evm/tokens/ethereum-sepolia:usdc/transfers"
        payload = {
            "recipient": reciepient_address,
            "amount": amount,
            #"signer": "external-wallet:"+signer_address
        }
        headers = {
            "X-API-KEY":self.api_key,
            "Content-Type": "application/json"
        }
        response = requests.post(url, json=payload, headers=headers)
        return response      
    
if __name__ == "__main__":
    crossmint = Crossmint()
    print(crossmint.get_balance("lordfourth"))
    print(crossmint.transfer("0xE28ae4711eaD88BE1Aa5d7E634D625F84477Fb5e","lordfourth","3.14"))
    #username is wallet name  # wallet_id is wallet address

