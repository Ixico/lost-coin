import wallet

# Krok 1: Stwórz portfel, jeśli jeszcze nie istnieje
password = "secure_password"
if not wallet.exists():
    wallet.create(password)

# Krok 2: Odblokuj portfel
wallet.unlock(password)

# Krok 3: Stwórz tożsamość
wallet.create_identity("miner1")