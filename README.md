# ONDC-Authenticator
This is Main App use for ONDC Authentication Subscription and sending requests to BG or Gateway to perform operation on BPP(Seller App) by Buyer App (BAP)
Here's an updated `README.md` for your open-source GitHub project, now referring to ONDC Gateway/Registry APIs and including the environment endpoints in a table format:

---

# ONDC Gateway/Registry API Authenticator and Request Sender

This Node.js module provides a simple way to generate **ed25519**-based authentication headers and send POST requests to **ONDC Gateway** and **Registry** APIs. It handles signature generation, digest creation for the request body, and sending the request with the appropriate headers.

## Features
- **ed25519 Signature Generation**: Uses the private key to sign the request.
- **ONDC Protocol Header Creation**: Automatically generates both `Authorization` and `X-Gateway-Authorization` headers according to ONDC specifications.
- **POST Request Sender**: Sends a JSON body as a POST request to the provided URL with generated headers.

## Requirements
- Node.js
- NPM or Yarn package manager
- ONDC Gateway/Registry-compliant API URL

## Installation

To install the module, use npm or yarn:

```bash
npm install noble-ed25519 axios
```

OR

```bash
yarn add noble-ed25519 axios
```

You will also need **crypto**, which is built into Node.js.

## Usage

To use the module, provide:
- The **API URL** to send the request.
- Your **subscriber ID** and **unique key ID**.
- Your **private key** (used to sign the request).
- The **body** of the request (JSON format).

Example usage:

```javascript
const { sendPostRequestWithAuth } = require('./ondc-auth');

// Sample request body and parameters
const url = 'https://staging.gateway.proteantech.in/search';  // Staging environment
const subscriberId = 'your-subscriber-id';
const uniqueKeyId = 'your-unique-key-id';
const privateKey = 'your-private-key';
const requestBody = {
  // Your JSON request body
};

(async () => {
  try {
    const response = await sendPostRequestWithAuth(url, subscriberId, uniqueKeyId, privateKey, requestBody);
    console.log('Response:', response);
  } catch (error) {
    console.error('Error:', error);
  }
})();
```

## API Endpoints

The ONDC Gateway and Registry APIs are available in different environments. Below are the available endpoints for staging, pre-production, and production:

| Environment      | Type      | Endpoint                                      |
|------------------|-----------|----------------------------------------------|
| **Staging**      | Gateway   | `https://staging.gateway.proteantech.in/search` |
|                  | Registry  | `https://staging.registry.ondc.org/lookup`     |
|                  | Registry  | `https://staging.registry.ondc.org/vlookup`    |
| **Pre-Production**| Gateway   | `https://preprod.gateway.ondc.org/search`      |
|                  | Registry  | `https://preprod.registry.ondc.org/ondc/lookup` |
|                  | Registry  | `https://preprod.registry.ondc.org/ondc/vlookup`|
| **Production**   | Gateway   | `https://prod.gateway.ondc.org/search`         |
|                  | Registry  | `https://prod.registry.ondc.org/ondc/lookup`   |
|                  | Registry  | `https://prod.registry.ondc.org/ondc/vlookup`  |

## How It Works

1. The module generates a **SHA-256 digest** from the request body.
2. It creates a **signing string** using the digest, current timestamp, and expiration timestamp.
3. The signing string is signed with the **ed25519 private key**, and the **Authorization** and **X-Gateway-Authorization** headers are generated.
4. The signed headers are included in the POST request to the provided ONDC Gateway or Registry URL.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

This `README.md` should provide all necessary details for users of your open-source project on GitHub!
