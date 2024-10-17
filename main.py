import getpass
import sys
import click

import node
import wallet

@click.group()
def application():
    pass

@application.command()
@click.option(
    "--password", prompt=True, hide_input=True,
    confirmation_prompt=True
)
def unlock_wallet(password):
    if not wallet.unlock(password):
        print("[ERROR] Invalid password.")
        unlock_wallet()
    else:
        print("Wallet unlocked successfully.")

@application.command()
@click.option(
    "--password", prompt=True, hide_input=True,
    confirmation_prompt=True, help="Enter strong password to create the wallet (min 12 characters)"
)
def create_wallet(password):
    if len(password) < 12:
        print('[ERROR] Password too short.')
        create_wallet()
    else:
        wallet.create(password)
        print("Wallet created successfully.")

@application.command()
@click.option('--registration_port', multiple=False, help="Port of the node it will join", type=int)
@click.option('--port', required=True, multiple=False, help="Port of this node", type=int)

def node_mode(port, registration_port):
    if registration_port is not None:
        node.create(port, registration_port)
    else:
        node.create(port, None)


if __name__ == '__main__':
    application()
    print('CLI Application Started...')

