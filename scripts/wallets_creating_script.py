import wallet
#use only once at start of the demo
def create_sample_wallet(node_id, password, identity_name):

    # Tworzenie lub odblokowywanie portfela
    if wallet.exists(node_id):
        print(f"Portfel dla węzła {node_id} już istnieje. Próba odblokowania...")
        wallet.unlock(node_id, password)
        print("Portfel został odblokowany.")
    else:
        print(f"Tworzenie nowego portfela dla węzła {node_id}...")
        wallet.create(node_id, password)
        print("Nowy portfel został utworzony.")

    # Dodawanie tożsamości
    identities = wallet.get_identities(node_id)
    if identity_name in identities:
        print(f"Tożsamość '{identity_name}' już istnieje w portfelu.")
    else:
        print(f"Tworzenie nowej tożsamości '{identity_name}'...")
        wallet.create_identity(node_id, identity_name)
        print(f"Tożsamość '{identity_name}' została utworzona.")

    # Wyświetlanie dostępnych tożsamości
    print(f"Dostępne tożsamości w portfelu węzła {node_id}: {wallet.get_identities(node_id)}")

# Wywołanie funkcji
create_sample_wallet("user1", "user1user1","user_id_1" )
create_sample_wallet("user2", "user2user2","user_id_2" )
create_sample_wallet("miner1", "miner1miner1","miner_id_1" )
