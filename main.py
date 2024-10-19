import getpass
import sys
import click

import node
import wallet

@click.group()
def application():
    pass

def unlock_wallet(password):
    if not wallet.unlock(password):
        print("[ERROR] Invalid password.")
        unlock_wallet()
    else:
        print("Wallet unlocked successfully.")

def create_wallet(password):
    if len(password) < 12:
        print('[ERROR] Password too short.')
        create_wallet()
    else:
        wallet.create(password)
        print("Wallet created successfully.")

@application.command()
@click.option('--registration_port', required=False, multiple=False, help="Port of the node it will join", type=int)
@click.option('--port', required=True, multiple=False, help="Port of this node", type=int)
@click.option(
    "--password", prompt=True, hide_input=True,
    confirmation_prompt=True, help="Wallet password"
)
def runup(port, registration_port, password):
    if wallet.exists():
        unlock_wallet(password)
    else:
        create_wallet(password)

    if registration_port is not None:
        node.create(port, registration_port)
    else:
        node.create(port, None)


if __name__ == '__main__':
    application()
    print('CLI Application Started...')

wallet.create_identity('polska2')