import requests
import json
from dataclasses import dataclass
from dataclass_wizard import YAMLWizard

@dataclass
class Config(YAMLWizard):
    access_token: str
    refresh_token: str
    client_id = "appie"
    user_agent = "Appie/8.22.3"
    host = "https://api.ah.nl"


def get_receipts(config: Config):
    url = config.host + "/mobile-services/v1/receipts"
    headers = {
            "Authorization": f"Bearer {config.access_token}",
            "Content-Type": "application/json",
            "User-Agent": config.user_agent
            }
    res = requests.get(url, headers = headers)
    return res


def get_receipt(config: Config, receipt_id: str):
    url = config.host + f"/mobile-services/v1/receipts/{receipt_id}"
    headers = {
            "Authorization": f"Bearer {config.access_token}",
            "Content-Type": "application/json",
            "User-Agent": config.user_agent
            }
    res = requests.get(url, headers = headers)
    return res


def refresh_token(config: Config):
    data = {
            "refreshToken" : config.refresh_token,
            "clientId" : config.client_id
            }
    url = config.host + "/mobile-auth/v1/auth/token/refresh"
    headers = {
            "Content-Type": "application/json",
            "User-Agent": config.user_agent
            }
    res = requests.post(url, data = data, headers = headers)
    return res.json()


def main(config: Config):
    receipts = get_receipts(config)
    
    # check auth
    if not receipts.ok:
        config.to_yaml_file("./config.yml.bak")
        res = refresh_token(config)
        config.access_token = res["access_token"]
        config.refresh_token = res["refresh_token"]
        config.to_yaml_file("./config.yml")
        print("Refreshed token")
        return

    # get receipts
    receipts = receipts.json()
    for receipt in receipts:
        print(receipt["transactionId"])
        trans_id = receipt["transactionId"]
        receipt = get_receipt(config, trans_id)
        print(receipt)
        with open(f"./receipts/{trans_id}.json", "w") as f:
            json.dump(receipt.json(), f, indent=1)


if __name__ == "__main__":
    config = Config.from_yaml_file("./config.yml")
    if isinstance(config, list):
        config = config[0]

    main(config)
