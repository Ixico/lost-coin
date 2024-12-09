import crypto


salt = '247e6a50dfb453ff6105b0fb76a7843f'
salt = bytes.fromhex(salt)

master_key = crypto.calculate_pbkdf2('polska123123123', salt).hex()
key = crypto.restore_key(master_key)
print('x')

#ValueError/IndexError/TypeError – When the given key cannot be parsed
# (possibly because the pass phrase is wrong).
