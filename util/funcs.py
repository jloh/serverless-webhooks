import hmac
import hashlib
from hashlib import sha1, sha256
from sys import hexversion

# Verifys Signatures against digest/messages
def verify_signature(secret, message, signature, digest):

    # Turn out AWS body into bytes
    message_string = str(message)
    message_bytes  = message_string.encode()

    # Our secret is already a string but we need to turn it into bytes
    secret_bytes   = secret.encode()

    # Create MAC
    mac = hmac.new(secret_bytes, msg=message_bytes, digestmod=eval(digest))

    # Compare our signature against our message
    if hmac.compare_digest(str(mac.hexdigest()), str(signature)):
        return True
    else:
        return False
