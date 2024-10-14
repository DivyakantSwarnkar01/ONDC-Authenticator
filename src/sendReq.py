# header_tool.py

import base64
import datetime
import json
import re
import os
import argparse
import uuid
from dotenv import load_dotenv
import nacl.encoding
import nacl.hash
from nacl.bindings import crypto_sign_ed25519_sk_to_seed
from nacl.signing import SigningKey, VerifyKey

# Load environment variables from .env file
load_dotenv()

PRIVATE_KEY = os.getenv('PRIVATE_KEY')
PUBLIC_KEY = os.getenv('PUBLIC_KEY')
UNIQUE_KEY_ID = os.getenv('UNIQUE_KEY_ID')
SUBSCRIBER_ID = os.getenv('SUBSCRIBER_ID')


def hash_message(msg: str) -> str:
    hasher = nacl.hash.blake2b
    digest = hasher(bytes(msg, 'utf-8'), digest_size=64, encoder=nacl.encoding.Base64Encoder)
    digest_str = digest.decode("utf-8")
    return digest_str


def create_signing_string(digest_base64: str, created: int = None, expires: int = None) -> str:
    if created is None:
        created = int(datetime.datetime.now().timestamp())
    if expires is None:
        expires = int((datetime.datetime.now() + datetime.timedelta(hours=1)).timestamp())
    signing_string = f"""(created): {created}
(expires): {expires}
digest: BLAKE-512={digest_base64}"""
    return signing_string


def sign_response(signing_key: str, private_key: str) -> str:
    private_key_bytes = base64.b64decode(private_key)
    seed = crypto_sign_ed25519_sk_to_seed(private_key_bytes)
    signer = SigningKey(seed)
    signed = signer.sign(bytes(signing_key, encoding='utf8'))
    signature = base64.b64encode(signed.signature).decode()
    return signature


def create_authorisation_header(request_body: str, private_key: str, unique_key_id: str, subscriber_id: str) -> str:
    created = int(datetime.datetime.now().timestamp())
    expires = int((datetime.datetime.now() + datetime.timedelta(hours=1)).timestamp())
    digest = hash_message(request_body)
    signing_key = create_signing_string(digest, created=created, expires=expires)
    signature = sign_response(signing_key, private_key)

    header = f'Signature keyId="{subscriber_id}|{unique_key_id}|ed25519",algorithm="ed25519",created="{created}",expires="{expires}",headers="(created) (expires) digest",signature="{signature}"'
    return header


def verify_response(signature: str, signing_key: str, public_key: str) -> bool:
    try:
        public_key_bytes = base64.b64decode(public_key)
        verify_key = VerifyKey(public_key_bytes)
        signature_bytes = base64.b64decode(signature)
        verify_key.verify(bytes(signing_key, 'utf8'), signature_bytes)
        return True
    except Exception as e:
        print(f"Verification failed: {e}")
        return False


def get_filter_dictionary_or_operation(filter_string: str) -> dict:
    filter_string_list = re.split(',', filter_string)
    filter_string_list = [x.strip(' ') for x in filter_string_list]
    filter_dictionary_or_operation = {}
    for fs in filter_string_list:
        splits = fs.split('=', maxsplit=1)
        if len(splits) != 2:
            continue  # Skip invalid entries
        key = splits[0].strip()
        value = splits[1].strip().strip('"')
        filter_dictionary_or_operation[key] = value
    return filter_dictionary_or_operation


def verify_header(auth_header: str, request_body_str: str, public_key: str) -> bool:
    header_parts = get_filter_dictionary_or_operation(auth_header.replace("Signature ", ""))
    try:
        created = int(header_parts['created'])
        expires = int(header_parts['expires'])
    except (KeyError, ValueError):
        print("Invalid or missing 'created'/'expires' in header.")
        return False

    current_timestamp = int(datetime.datetime.now().timestamp())
    if not (created <= current_timestamp <= expires):
        print("Header has expired or is not yet valid.")
        return False

    digest = hash_message(request_body_str)
    signing_key = create_signing_string(digest, created=created, expires=expires)
    return verify_response(header_parts.get('signature', ''), signing_key, public_key=public_key)


def generate_header(request_body: str) -> str:
    header = create_authorisation_header(
        request_body=request_body,
        private_key=PRIVATE_KEY,
        unique_key_id=UNIQUE_KEY_ID,
        subscriber_id=SUBSCRIBER_ID
    )
    return header


def main():
    parser = argparse.ArgumentParser(description="Authorization Header Tool")
    subparsers = parser.add_subparsers(dest='command', help='Commands: generate, verify')

    parser_generate = subparsers.add_parser('generate', help='Generate authorization header')
    parser_generate.add_argument('--request_body', type=str, help='Path to JSON request body file')

    parser_verify = subparsers.add_parser('verify', help='Verify authorization header')
    parser_verify.add_argument('--auth_header', type=str, help='Authorization header string')
    parser_verify.add_argument('--request_body', type=str, help='Path to JSON request body file')
    parser_verify.add_argument('--public_key', type=str, help='Public key (Base64 encoded)')

    args = parser.parse_args()

    if args.command == 'generate':
        if args.request_body:
            try:
                with open(args.request_body, 'r') as f:
                    request_body = f.read()
            except FileNotFoundError:
                print(f"File not found: {args.request_body}")
                return
        else:
            # Default request body as a single inline string without spaces and with dynamic fields
            timestamp_iso = datetime.datetime.now(datetime.timezone.utc).isoformat() + 'Z'
            message_id = str(uuid.uuid4())
            transaction_id = str(uuid.uuid4())
            request_body_inline = '{"context":{"domain":"nic2004:52110","country":"IND","city":"std:011","action":"search","core_version":"0.9.1","bap_id":"www.indiacost.in","bap_uri":"https://www.indiacost.in/bapl","transaction_id":"'+transaction_id+'","message_id":"'+message_id+'","timestamp":"'+timestamp_iso+'","ttl":"PT1H"},"message":{"intent":{"fulfillment":{"start":{"location":{"gps":"28.6129,77.2295"}},"end":{"location":{"gps":"28.6310,77.2167"}}}}}}'

            request_body = request_body_inline
            print("Using default request body with dynamic fields:")
            print(request_body)  # Print the JSON request body

        # Ensure the JSON is valid and minified
        try:
            request_body_min = json.dumps(json.loads(request_body), separators=(',', ':'))
        except json.JSONDecodeError as e:
            print(f"Invalid JSON request body: {e}")
            return

        header = generate_header(request_body_min)
        print("Generated Authorization Header:")
        print(header)

    elif args.command == 'verify':
        if not args.auth_header or not args.request_body or not args.public_key:
            print("For verification, please provide --auth_header, --request_body, and --public_key.")
            return

        try:
            with open(args.request_body, 'r') as f:
                request_body = f.read()
        except FileNotFoundError:
            print(f"File not found: {args.request_body}")
            return

        # Ensure the JSON is valid and minified
        try:
            request_body_min = json.dumps(json.loads(request_body), separators=(',', ':'))
        except json.JSONDecodeError as e:
            print(f"Invalid JSON request body: {e}")
            return

        is_valid = verify_header(args.auth_header, request_body_min, args.public_key)
        print(f"Verification result: {is_valid}")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
