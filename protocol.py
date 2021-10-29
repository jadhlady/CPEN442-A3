import random
from tkinter.constants import TRUE
import hashlib

# local import from "exceptions.py"
from exceptions import IntegrityVerificationError, AuthenticationError

class Protocol:
    # Initializer (Called from app.py)
    # TODO: MODIFY ARGUMENTS AND LOGIC AS YOU SEEM FIT
    def __init__(self, sharedSecret):
        self.SetSharedSecret(sharedSecret)
        pass

    ###############     PRIVATE METHODS     ###############

    def _CalculateHash(self, message):
        msg = str(message)
        msg_bytes = msg.encode()
        return hashlib.sha256(msg_bytes).hexdigest()


    def _VerifyIntegrity(self, hash_message):
        """ This cryptogrpahic hash function is implemented using the SHA-256 algorithm.
        It is used to check the integrity of the messages. """

        # Extract the hash value from string
        hash_value = hash_message[-65:-1]
        orig_len = len(hash_message)
        message = hash_message[2:orig_len - 65]

        received_hash = self._CalculateHash(str(message))

        if (received_hash != hash_value):
            return [False, message]

        return [True, message]


    def _AuthenticateSender(self):
        """ This function is implemented using the Diffie-Hellman algorithm.
        It is used to authenticate the sender of the message received. """
        return True


    ########################################################


    # Creating the initial message of your protocol (to be send to the other party to bootstrap the protocol)
    # TODO: IMPLEMENT THE LOGIC (MODIFY THE INPUT ARGUMENTS AS YOU SEEM FIT)
    def GetProtocolInitiationMessage(self):
        self.p = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF
        self.g = 2
        self.private_val = random.getrandbits(2048) 
        self.public_val = pow(self.g,self.private_val,self.p)
        return self.public_val


    # Checking if a received message is part of your protocol (called from app.py)
    # TODO: IMPLMENET THE LOGICs
    def IsMessagePartOfProtocol(self, message):
        return False


    # Processing protocol message
    # TODO: IMPLMENET THE LOGIC (CALL SetSessionKey ONCE YOU HAVE THE KEY ESTABLISHED)
    # THROW EXCEPTION IF AUTHENTICATION FAILS
    def ProcessReceivedProtocolMessage(self, message):
         #TODO: decrypt and sanitize message
        received_public_key = None
        session_key = pow(received_public_key, self.private_val, self.p)
        self._SetSessionKey(session_key)
        pass
    

    # Setting the shared secret to encrypt protocol messages
    def SetSharedSecret(self, sharedSecret):
        """ This function sets the long-term shared secret for the protocol
        when it receives an update from the application."""
        self._sharedSecret = sharedSecret


    # Setting the key for the current session
    def _SetSessionKey(self, key):
        """ This function sets the session key secret (intended to be used for
        this session only."""
        self._sessionKey = key


    # Encrypting messages
    # TODO: IMPLEMENT ENCRYPTION WITH THE SESSION KEY (ALSO INCLUDE ANY NECESSARY INFO IN THE ENCRYPTED MESSAGE FOR INTEGRITY PROTECTION)
    # RETURN AN ERROR MESSAGE IF INTEGRITY VERITIFCATION OR AUTHENTICATION FAILS
    def EncryptAndProtectMessage(self, plain_text):
        try:
            authenticated = self._AuthenticateSender()

            if (not authenticated):
                raise AuthenticationError

            # TODO: Use the current user's private key to protect the message before sending
            signed_plaintext = str(plain_text)

            hash_msg = self._CalculateHash(signed_plaintext)

            cipher_text = signed_plaintext + hash_msg  # Append message digest for verification
            return cipher_text

        except AuthenticationError as error:
            return "ENCRYPTION ERROR: AUTHENTICATION FAILED."
        

    # Decrypting and verifying messages
    # TODO: IMPLEMENT DECRYPTION AND INTEGRITY CHECK WITH THE SESSION KEY
    # RETURN AN ERROR MESSAGE IF INTEGRITY VERITIFCATION OR AUTHENTICATION FAILS
    def DecryptAndVerifyMessage(self, cipher_text):
        try:
            authenticated = self._AuthenticateSender()

            if (not authenticated):
                raise AuthenticationError
            
            # TODO: Remove the signature layer here to get the message appended with its hash value
            # before verifying the hash and message
            hash_msg = str(cipher_text)

            integrity_verified, signed_message = self._VerifyIntegrity(hash_msg)

            if (not integrity_verified):
                raise IntegrityVerificationError

            # decrypt the signed message
            message = str(signed_message)

            return message

        except IntegrityVerificationError as error:
            return "ENCRYPTION ERROR: INTEGRITY VERIFICATION FAILED."
        except AuthenticationError as error:
            return "ENCRYPTION ERROR: AUTHENTICATION FAILED." 
