Here's a comprehensive `README.md` file for your `header_tool.py` project, detailing its purpose, usage, and functionality for generating and verifying ONDC authorization headers:

```markdown
# ONDC Authorization Header Tool

## Overview

The ONDC Authorization Header Tool is a command-line utility for generating and verifying authorization headers compliant with the Open Network for Digital Commerce (ONDC) standards. This tool enables developers to easily create authorization headers required for API requests and validate these headers to ensure secure communications.

## Features

- **Generate Authorization Header**: Create a signature-based authorization header for API requests using a specified JSON request body.
- **Verify Authorization Header**: Validate an existing authorization header against a provided JSON request body and public key.
- **Environment Configuration**: Load private keys, public keys, unique IDs, and subscriber IDs from an `.env` file for secure storage of sensitive information.
- **Support for Dynamic JSON**: Automatically generates a default JSON request body with dynamic fields if no request body is specified.

## Prerequisites

Before using this tool, ensure you have the following:

- Python 3.x installed on your system.
- Required Python packages. Install them using:

```bash
pip install python-dotenv PyNaCl
```

- A `.env` file containing the following variables:

```
PRIVATE_KEY=<YourPrivateKeyBase64>
PUBLIC_KEY=<YourPublicKeyBase64>
UNIQUE_KEY_ID=<YourUniqueKeyID>
SUBSCRIBER_ID=<YourSubscriberID>
```

## Usage

### Command-Line Interface

The tool can be executed from the command line using the following syntax:

```bash
python header_tool.py <command> [options]
```

### Commands

#### 1. Generate Authorization Header

To generate an authorization header, use the `generate` command with an optional request body file:

```bash
python header_tool.py generate --request_body <path_to_json_file>
```

- If you do not provide a request body file, the tool will generate a default request body with dynamic fields.

#### 2. Verify Authorization Header

To verify an existing authorization header, use the `verify` command:

```bash
python header_tool.py verify --auth_header "<your_authorization_header>" --request_body <path_to_json_file> --public_key "<your_public_key>"
```

- Ensure to provide all three arguments: `--auth_header`, `--request_body`, and `--public_key`.

### Examples

#### Generating an Authorization Header

```bash
python header_tool.py generate --request_body body.json
```

Output:
```
Generated Authorization Header:
Signature keyId="www.indiacost.in|475fa200-e957-4966-ab79-597de00f6e03|ed25519",algorithm="ed25519",created="1728932010",expires="1728935610",headers="(created) (expires) digest",signature="0FwuNiRKHCn0iXY1Tid8+LCg6fagyq8fwZwFsTUwpUpJRDPsiPyXoTuiZKAWuVUGGe1qNlLfBuesOR+AifOvBQ=="
```

#### Verifying an Authorization Header

```bash
python header_tool.py verify --auth_header "Signature keyId=..." --request_body body.json --public_key "atHDSd14uEFrv+i2CyHSNxl61QUXbhVYHTlUOkWwCkY="
```

Output:
```
Verification result: True
```

## Error Handling

- **File Not Found**: If the specified request body file does not exist, the tool will print an error message and terminate.
- **Invalid JSON**: If the JSON request body is malformed, an error message will be displayed indicating the nature of the error.

## Contribution

Contributions to enhance the functionality of this tool are welcome! Please open an issue or submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

## Author

Developed by [Your Name](https://yourwebsite.com).
```

### Instructions

- Replace `<YourPrivateKeyBase64>`, `<YourPublicKeyBase64>`, `<YourUniqueKeyID>`, and `<YourSubscriberID>` with the actual keys and IDs you'll be using.
- Update the author information at the end of the document with your name and website if desired.

This `README.md` file should provide clear guidance for users on how to use your command-line tool for ONDC authorization header generation and verification.
