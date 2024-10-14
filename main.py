import crypto
import wallet

# todo: better cli, getpass, loading process for time consuming operations, better navigation using keyboard

if wallet.exists():
    password = input('Enter password to unlock the wallet:\n')
    master_key = wallet.unlock(password)
    print("Wallet unlocked successfully.")
    print("1. Use identity")
    print("2. Create new identity")
    option = input()
    if option == '1':
        print("ok lets use (to be implemented)")
        for index, filename in enumerate(wallet.get_identities(), start=1):
            print(f"{index}. {filename}")
    if option == '2':
        wallet.create_identity(input("Enter new identity name:\n"))
        print("Identity created successfully!")
    else:
        exit()
else:
    password = input('Enter strong password to create the wallet (min 12 characters):\n')
    if not crypto.is_password_strong(password):
        print("Password is too short.")
        exit()
    wallet.create(password)

