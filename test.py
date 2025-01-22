import os
#os.environ["SSL_CERT_DIR"] = "/usr/local/share/ca-certificates"

from twitter.account import Account
from dotenv import load_dotenv

load_dotenv()

TELEPORT_AUTH = os.getenv("TELEPORT_AUTH")
def main():
    account = Account(cookies={"ct0": "f40e5f6d89b35d0ea1fc078d7964e80bd6507da443f8e81c30e132f27d2505d3c1f458c800e1b807c17d11b2898933ee29a6875ae0607fd551cab0460b099778d72903f8d6a67e2c4b9308de3ad4af12", 
                               "auth_token": TELEPORT_AUTH})
    inbox = account.dm_inbox()
    print(inbox)

if __name__ == "__main__":
    main()
