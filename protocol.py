import random
from tkinter.constants import TRUE
import hashlib
import time
from enum import Enum
# from Crypto.Cipher import AES

# local import from "exceptions.py"
from exceptions import IntegrityVerificationError, AuthenticationError

class Protocol:
    # Initializer (Called from app.py)
    # TODO: MODIFY ARGUMENTS AND LOGIC AS YOU SEEM FIT
    def __init__(self, sharedSecret):
        # Server-mode by default until user selects a mode
        self._identifier = Protocol.ClientOrServerIdentifier.SERVER

        self.SetSharedSecret(sharedSecret)
        self.messageCount = 0
        self.p = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF
        self.g = 2
        self.private_val = random.getrandbits(2048)
        pass


    class ClientOrServerIdentifier(Enum):
        CLIENT = "CLIENT"
        SERVER = "SERVER"


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
    # TODO: IMPLEMENT THE LOGIC (MODIFY THE INPUT ARGUMENTS AS YOU SEEM FIT)
    def GetProtocolInitiationMessage(self):
        if self._identifier == Protocol.ClientOrServerIdentifier.CLIENT:
            if not self.messageCount:
                print("CLIENT: Send first protocol message")
                self.public_val = pow(self.g,self.private_val,self.p)
                self.nonce = self.GetRandomChallenge() # Set nonce to current time
                return "Im Client," + str(self.nonce)
            else:
                print("CLIENT: Send third protocol message")
                self.public_val = pow(self.g,self.private_val,self.p)
                ServerNonce = str(self.nonce)
                return self.EncryptProtocolMessage("Client" +"," + ServerNonce + "," + self.public_val)
        else:
            print("SERVER: Send second protocol message")
            self.public_val = pow(self.g,self.private_val,self.p)
            ClientNonce, self.nonce = str(self.nonce), str(self.GetRandomChallenge())
            return self.nonce + "," + self.EncryptProtocolMessage("Server" +"," + ClientNonce + "," + self.public_val)


    # Checking if a received message is part of your protocol (called from app.py)
    # TODO: IMPLMENET THE LOGICs
    def IsMessagePartOfProtocol(self, message):
        if(message.find("Protocol:", 0, len("Protocol:")) != -1):
            return True  # if the message contains a protocol flag
        else:
            return False


    def EncryptProtocolMessage(self, message):
        return message

    def DecryptProtocolMessage(self, message):
        return message

    # Processing protocol message
    # TODO: IMPLMENET THE LOGIC (CALL SetSessionKey ONCE YOU HAVE THE KEY ESTABLISHED)
    # THROW EXCEPTION IF AUTHENTICATION FAILS
    def ProcessReceivedProtocolMessage(self, message):
        if self._identifier == Protocol.ClientOrServerIdentifier.SERVER:
            if self.messageCount == 0:
                print("Server receives first protocol message")
                try:
                    messageArray = message.split(",")
                    if (messageArray[0] != "Im Client"):
                        raise AuthenticationError()
                    self.nonce = messageArray[1]
                    self.messageCount = 1
                except AuthenticationError:
                    return "AUTHENTICATION ERROR: FAILED TO ESTABLISH CONNECTION"
            else:
                print("Server receives third protocol message")
                messageArray = self.DecryptProtocolMessage(message).split(",")
                try:
                    if (messageArray[0] != "Client"):
                        raise AuthenticationError()
                    elif (self.nonce != messageArray[1]):
                        raise AuthenticationError()
                    self.ClientDHKey = messageArray[2]
                except AuthenticationError:
                    return "AUTHENTICATION ERROR: FAILED TO ESTABLISH CONNECTION"

                # Server calculates session key
                self._SetSessionKey(pow(self.ClientDHKey, self.private_val, self.p))
        
        else:
            print("Client receives second protocol message")
            nonceNew = message[:message.find(",")]
            messageArray = self.DecryptProtocolMessage(message).split(",")
            try:
                if (messageArray[0] != "Server"):
                    raise AuthenticationError()
                elif (self.nonce != messageArray[1]):
                    raise AuthenticationError()
                self.ServerDHKey = messageArray[2]
            except AuthenticationError:
                return "AUTHENTICATION ERROR: FAILED TO ESTABLISH CONNECTION"

            # Client calculates session key
            self._SetSessionKey(pow(self.ServerDHKey, self.private_val, self.p))

            self.messageCount = 1
            
            return True

        # TODO: add this back somewhere
        # # Verify we did not receive our own message
        # if (identifier == self._identifier) or (identifier not in Protocol.ClientOrServerIdentifier.__members__):
        #     raise AuthenticationError
    

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
