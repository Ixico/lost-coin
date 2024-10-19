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
    confirmation_prompt=True, help="Enter strong password to create the wallet (min 12 characters)"
)
def createwallet(password):
    if len(password) < 12:
        print('[ERROR] Password too short.')
    else:
        wallet.create(password)
        print("Wallet created successfully.")
def unlock_wallet(password):
    if not wallet.unlock(password):
        print("[ERROR] Invalid password.")
    else:
        print("Wallet unlocked successfully.")



@application.command()
@click.option(
    "--password", prompt=True, hide_input=True,
    confirmation_prompt=True, help="Enter the password for appropriate wallet")
@click.option(
    "--identity", type=click.Choice(['view', 'add'], case_sensitive=True),
    required=True,
    help="Select if you want to view existing entities or add a new one"
)
def identitymanagement(password, identity):
    unlock_wallet(password)
    if identity == 'view':
        identities = wallet.get_identities()
        print(identities)
    elif identity == 'add':
        phrase = click.prompt("Please enter the phrase", hide_input=False, confirmation_prompt=True)
        wallet.create_identity(phrase)



@application.command()
@click.option('--registration_port', required=False, multiple=False, help="Port of the node it will join", type=int)
@click.option('--port', required=True, multiple=False, help="Port of this node", type=int)
@click.option(
    "--password", prompt=True, hide_input=True,
    confirmation_prompt=True, help="Wallet password"
)
def runup(port, registration_port, password):
    unlock_wallet(password)
    if registration_port is not None:
        node.create(port, registration_port)
    else:
        node.create(port, None)


if __name__ == '__main__':
    application()
    print('CLI Application Started...')
