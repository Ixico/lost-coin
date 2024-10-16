import getpass
import sys

import keyboard

import node
import wallet

args = sys.argv
if len(args) == 2:
    port = int(args[1])
    registration_port = None
elif len(args) == 3:
    port = int(args[1])
    registration_port = int(args[2])
else:
    print('[ERROR] Usage: main.py <port> <registration_port?>')
    exit(-1)


def menu(header, options):
    print(f"\n---{header}---")
    for index, option in enumerate(options, start=1):
        print(f"{index}. {option}")
    while True:
        key = keyboard.read_event()
        if key.event_type == keyboard.KEY_DOWN and key.name.isdigit():
            result = int(key.name)
            if result <= len(options):
                return result


def unlock_wallet():
    password = getpass.getpass('Enter password to unlock the wallet:\n')
    if not wallet.unlock(password):
        print("[ERROR] Invalid password.")
        unlock_wallet()
    else:
        print("Wallet unlocked successfully.")


def create_wallet():
    password = getpass.getpass('Enter strong password to create the wallet (min 12 characters):\n')
    if len(password) < 12:
        print('[ERROR] Password too short.')
        create_wallet()
    else:
        wallet.create(password)
        print("Wallet created successfully.")



print("LOST-COIN")
if wallet.exists():
    unlock_wallet()
else:
    create_wallet()
while True:
    option = menu('MENU', ['Use identity', 'Create new identity'])
    if option == 1:
        identities = wallet.get_identities()
        option = menu('YOUR IDENTITIES', identities)
        print(f"\nCreated node for identity {identities[option - 1]}")
        node.create(port, registration_port)
