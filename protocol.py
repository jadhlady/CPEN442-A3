from random import random
from Crypto.Random import random
import hashlib
import time
from enum import Enum
import AESEncrypt

# local import from "exceptions.py"
from exceptions import IntegrityVerificationError, AuthenticationError

class Protocol:
    # Initializer (Called from app.py)
    def __init__(self, sharedSecret):
        # Server-mode by default until user selects a mode
        self._identifier = Protocol.ClientOrServerIdentifier.SERVER

        self.SetSharedSecret(sharedSecret)
        self.messageCount = 0
        self.p = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF
        self.g = 2
        self.private_val = random.getrandbits(2048)
        pass


    class ClientOrServerIdentifier(str, Enum):
        CLIENT = "CLIENT"
        SERVER = "SERVER"


    ###############     PRIVATE METHODS     ###############

    def _CalculateHash(self, message):
        msg = str(message)
        msg_bytes = msg.encode()
        return hashlib.sha256(msg_bytes).hexdigest()


    def _VerifyIntegrity(self, received_hash, message):
        """ This cryptogrpahic hash function is implemented using the SHA-256 algorithm.
        It is used to check the integrity of the messages. """

        calculated_hash = self._CalculateHash(str(message))

        if (received_hash != calculated_hash):
            return False

        return True


    def _ExtractHash(self, message_with_hash):
        """ This function extracts the hashed plaintext value out of the last 64 characters of
        the message, which will be used to verify the integrity of the message."""
        return message_with_hash[-64:]


    def _RemoveHash(self, message_with_hash):
        """ This function removes the hash value from the message."""
        orig_len = len(message_with_hash)
        return message_with_hash[:orig_len - 64]


    def _AuthenticateSender(self):
        """ This function is implemented using the Diffie-Hellman algorithm.
        It is used to authenticate the sender of the message received. """
        return True


    ########################################################


    # Uses timestamp to generate a unique nonce challenge to prevent replay
    # attacks.
    def GetRandomChallenge(self):
        return str(time.time())


    # Sets the client or server identifier for this protocol user to identify
    # if messages are being sent back to ourselves.
    def SetClientOrServerIdentifier(self, identifier):
        self._identifier = identifier


    # Creating the initial message of your protocol (to be send to the other party to bootstrap the protocol)
    # This is only the first part of the authentication and DH process
    # Other functions will take over the next parts of the authentication and DH process
    def GetProtocolInitiationMessage(self):
        if self._identifier == Protocol.ClientOrServerIdentifier.CLIENT:
            if self.messageCount == 0:
                # Sending protocol message 1: "Im Client, $nonce"
                self.public_val = pow(self.g,self.private_val,self.p)
                self.nonce = self.GetRandomChallenge() # Set nonce to current time
                return "Im Client," + str(self.nonce)
            else:
                # Sending protocol message 3: E("Client, $ServerNonce, $public_val", _sharedSecret)
                self.public_val = pow(self.g,self.private_val,self.p)
                ServerNonce = str(self.nonce)
                return self.EncryptMessage(self._identifier + "," + ServerNonce + "," + str(self.public_val), self._sharedSecret)
        else:
            if self.messageCount == 0:
                # Tell client to start protocol
                return "Im Server"
            else:
                # Sending protocol message 2: nonce, E("Server, $ClientNonce, $public_val", _sharedSecret)
                self.public_val = pow(self.g,self.private_val,self.p)
                ClientNonce, self.nonce = str(self.nonce), str(self.GetRandomChallenge())
                return self.nonce + "," + self.EncryptMessage(self._identifier + "," + ClientNonce + "," + str(self.public_val), self._sharedSecret)


    # Checking if a received message is part of your protocol (called from app.py)
    def IsMessagePartOfProtocol(self, message):
        if(message.find("Protocol:", 0, len("Protocol:")) != -1):
            return True  # if the message contains a protocol flag
        else:
            return False


    # Default key shared secret, override with sessionKey for authenticated comms
    def EncryptMessage(self, message, key):
        AES = AESEncrypt.AESCipher(key)
        encrypted = AES.encrypt(message)
        return encrypted


    def DecryptMessage(self, message, key):
        AES = AESEncrypt.AESCipher(key)
        decrypted = AES.decrypt(message)
        return decrypted


    # Processing protocol message
    # THROW EXCEPTION IF AUTHENTICATION FAILS
    def ProcessReceivedProtocolMessage(self, message):
        if self._identifier == Protocol.ClientOrServerIdentifier.SERVER:
            if self.messageCount == 0:
                # Processing protocol message 1
                try:
                    messageArray = message.split(",")
                    if (messageArray[0] != "Im Client"):
                        raise AuthenticationError()
                    self.nonce = messageArray[1]
                    self.messageCount = 1
                except AuthenticationError:
                    return "AUTHENTICATION ERROR: FAILED TO ESTABLISH CONNECTION"

                return True
            else:
                # Processing protocol message 3
                messageArray = self.DecryptMessage(message, self._sharedSecret).split(",")
                try:
                    if (messageArray[0] != Protocol.ClientOrServerIdentifier.CLIENT):
                        raise AuthenticationError()
                    elif (self.nonce != messageArray[1]):
                        raise AuthenticationError()
                    
                    try:
                        self.ClientDHKey = int(messageArray[2])
                    except ValueError:
                        raise AuthenticationError
                except AuthenticationError:
                    return "AUTHENTICATION ERROR: FAILED TO ESTABLISH CONNECTION"

                # Server calculates session key
                self._SetSessionKey(pow(self.ClientDHKey, self.private_val, self.p))

                # Protocol is finished, do not respond
                return False
        else:
            if message == "Im Server":
                # Start protocol
                return True

            # Processing message 2: nonce, E("Server, $ClientNonce, $public_val", _sharedSecret)
            nonceNew = message.split(',')[0]
            encryptedMessage = message.split(',')[1]
            messageArray = self.DecryptMessage(encryptedMessage, self._sharedSecret).split(",")
            try:
                if (messageArray[0] != Protocol.ClientOrServerIdentifier.SERVER):
                    raise AuthenticationError()
                elif (self.nonce != messageArray[1]):
                    raise AuthenticationError()

                try:
                    self.ServerDHKey = int(messageArray[2])
                except ValueError:
                    raise AuthenticationError
            except AuthenticationError:
                return "AUTHENTICATION ERROR: FAILED TO ESTABLISH CONNECTION"

            # Client calculates session key
            self._SetSessionKey(pow(self.ServerDHKey, self.private_val, self.p))

            # Store nonce to encrypt it later
            self.nonce = nonceNew

            self.messageCount = 1
            
            return True
    

    # Setting the shared secret to encrypt protocol messages
    def SetSharedSecret(self, sharedSecret):
        """ This function sets the long-term shared secret for the protocol
        when it receives an update from the application."""
        self._sharedSecret = sharedSecret


    # Setting the key for the current session
    def _SetSessionKey(self, key):
        """ This function sets the session key secret (intended to be used for
        this session only."""
        self._sessionKey = str(key)


    # Encrypting messages
    # RETURN AN ERROR MESSAGE IF INTEGRITY VERITIFCATION OR AUTHENTICATION FAILS
    def EncryptAndProtectMessage(self, plain_text):
        try:
            authenticated = self._AuthenticateSender()

            if (not authenticated):
                raise AuthenticationError

            hash_msg = self._CalculateHash(plain_text) # Append message digest for verification
            cipher_text = self.EncryptMessage(plain_text + hash_msg, self._sessionKey)

            return cipher_text

        except AuthenticationError as error:
            return "ENCRYPTION ERROR: AUTHENTICATION FAILED."
        

    # Decrypting and verifying messages
    # RETURN AN ERROR MESSAGE IF INTEGRITY VERITIFCATION OR AUTHENTICATION FAILS
    def DecryptAndVerifyMessage(self, cipher_text):
        try:
            authenticated = self._AuthenticateSender()

            if (not authenticated):
                raise AuthenticationError

            message_with_hash = self.DecryptMessage(cipher_text, self._sessionKey)
            
            received_hash = self._ExtractHash(message_with_hash)
            message = self._RemoveHash(message_with_hash)

            integrity_verified = self._VerifyIntegrity(received_hash, message)

            if (not integrity_verified):
                raise IntegrityVerificationError

            return message

        except IntegrityVerificationError as error:
            return "ENCRYPTION ERROR: INTEGRITY VERIFICATION FAILED."
        except AuthenticationError as error:
            return "ENCRYPTION ERROR: AUTHENTICATION FAILED." 
