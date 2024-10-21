import click

import node
import wallet
from common import CommonException


@click.group()
def application():
    pass

@application.command()
def createwallet():
    if not wallet.exists():
        password = click.prompt("Enter strong password to create the wallet (min 12 characters)",hide_input=True, confirmation_prompt=True)
        if len(password) < 12:
            print('Password too short.')
        else:
            wallet.create(password)
            print("Wallet created successfully.")
    else:
        print('Wallet already exists')

def unlock_wallet(password):
    try:
        wallet.unlock(password)
        print("Wallet unlocked successfully.")
    except CommonException:
        print('invalid password')
        exit()

@application.command()
@click.option(
    "--password", prompt=True, hide_input=True, help="Enter the password for appropriate wallet")
@click.option(
    "--identity", type=click.Choice(['view', 'add'], case_sensitive=True),
    required=True,
    help="Select if you want to view existing entities or add a new one"
)
def identitymanagement(password, identity):
    unlock_wallet(password)
    identities = wallet.get_identities()
    if identity == 'view':
        print(identities)
    elif identity == 'add':
        phrase = click.prompt("Please enter the phrase", hide_input=False, confirmation_prompt=True)
        if phrase in identities:
            print(f'Identity {phrase} already exists.')
            exit()
        wallet.create_identity(phrase)



@application.command()
@click.option('--registration_port', required=False, multiple=False, help="Port of the node it will join", type=int)
@click.option('--port', required=True, multiple=False, help="Port of this node", type=int)
@click.option(
    "--password", prompt=True, hide_input=True,  help="Wallet password"
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
