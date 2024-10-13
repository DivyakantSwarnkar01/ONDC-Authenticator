import base64
import datetime
import json
import uuid  # Import UUID for generating unique IDs
import nacl.encoding
import nacl.hash
import requests  # Import requests for sending HTTP requests
from nacl.bindings import crypto_sign_ed25519_sk_to_seed
from nacl.signing import SigningKey, VerifyKey


def hash_message(msg: str):
    HASHER = nacl.hash.blake2b
    digest = HASHER(bytes(msg, 'utf-8'), digest_size=64, encoder=nacl.encoding.Base64Encoder)
    digest_str = digest.decode("utf-8")
    return digest_str


def create_signing_string(digest_base64, created, expires):
    signing_string = f"""(created): {created}
(expires): {expires}
digest: BLAKE-512={digest_base64}"""
    return signing_string


def sign_response(signing_key, private_key):
    private_key64 = base64.b64decode(private_key)
    seed = crypto_sign_ed25519_sk_to_seed(private_key64)
    signer = SigningKey(seed)
    signed = signer.sign(bytes(signing_key, encoding='utf8'))
    signature = base64.b64encode(signed.signature).decode()
    return signature


def verify_response(signature, signing_key, public_key):
    try:
        public_key64 = base64.b64decode(public_key)
        VerifyKey(public_key64).verify(bytes(signing_key, 'utf8'), base64.b64decode(signature))
        return True
    except Exception:
        return False


def generate_time_info():
    """Generate unique transaction ID, message ID, and current Unix timestamp."""
    transaction_id = str(uuid.uuid4())  # Generates a unique transaction ID
    message_id = str(uuid.uuid4())       # Generates a unique message ID
    timestamp_unix = int(datetime.datetime.now().timestamp())  # Current timestamp in Unix format
    return transaction_id, message_id, timestamp_unix


def generate_time_stamps():
    """Generate Unix timestamps for created and expires."""
    created = int(datetime.datetime.now().timestamp())  # Current timestamp for created
    expires = created + 3600  # Set expires to one hour later
    return created, expires


def create_authorisation_header(request_body, created, expires, subscriber_id, unique_key_id, private_key):
    # Create the signing key from the request body
    signing_key = create_signing_string(hash_message(json.dumps(request_body, separators=(',', ':'))),
                                         created=created, expires=expires)
    
    # Sign the response using the provided private key
    signature = sign_response(signing_key, private_key=private_key)

    # Create the authorization header
    header = f'Signature keyId="{subscriber_id}|{unique_key_id}|ed25519",algorithm="ed25519",created=' \
             f'"{created}",expires="{expires}",headers="(created) (expires) digest",signature="{signature}"'
    
    return header


def send_request(url, headers, json_body):
    """Send a POST request with headers and JSON body."""
    response = requests.post(url, headers=headers, json=json_body)
    return response


# Generate unique transaction ID, message ID, and Unix timestamp
transaction_id, message_id, timestamp_unix = generate_time_info()

# Define ISO formatted timestamp for the request body
timestamp_iso = datetime.datetime.fromtimestamp(timestamp_unix).isoformat()  # Convert to ISO format

# Define the request body with the generated IDs
request_body = {
    "context": {
        "domain": "nic2004:60212",
        "country": "IND",
        "city": "Kochi",
        "action": "search",
        "core_version": "0.9.1",
        "bap_id": "www.indiacost.in", #Your unique URL that is whitelisted on ONDC adjust it as per need.
        "bap_uri": "/bapl",  # Adjusted to use staging_url as per requirement
        "transaction_id": transaction_id,
        "message_id": message_id,
        "timestamp": timestamp_iso,  # ISO formatted timestamp
        "ttl": "P1M"
    },
    "message": {
        "intent": {
            "fulfillment": {
                "start": {
                    "location": {
                        "gps": "10.108768,76.347517"
                    }
                },
                "end": {
                    "location": {
                        "gps": "10.102997,76.353480"
                    }
                }
            }
        }
    }
}

# Generate created and expires timestamps
created_time, expires_time = generate_time_stamps()

# Hard-coded values for subscriber_id, unique_key_id, and private_key
subscriber_id = "YOUR_SUBSCRIBER_ID"  # Hard-coded subscriber ID
unique_key_id = "Your_UNIQUE_KEY_ID"  # Hard-coded unique key ID
private_key = "YOUR_PRIVATE_KEY"       # Hard-coded private key

# Generate authorization header
auth_header = create_authorisation_header(request_body=request_body, created=created_time, expires=expires_time,
                                          subscriber_id=subscriber_id, unique_key_id=unique_key_id, private_key=private_key)

# Hard-coded URL to send the request
url = "https://example.com/api"  # Replace with your desired URL

# Send the request and get the response
response = send_request(url, headers={"Authorization": auth_header, "Content-Type": "application/json"}, json_body=request_body)

# Print the response
print(response.status_code)
print(response.json())
