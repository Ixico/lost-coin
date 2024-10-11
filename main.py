import os
import crypto, wallet
import getpass

print(crypto.keys())
if wallet.exists():
    password = input('Enter password to unlock the wallet:\n')
    metadata = wallet.get_metadata()
    key_metadata = crypto.derive_valid_key(password, metadata)
    print('ok')
else:
    password = input('Enter strong password to create the wallet (min 12 characters):\n')
    if not crypto.is_password_strong(password):
        print("Password is too short.")
        exit()
    wallet.create(password)

