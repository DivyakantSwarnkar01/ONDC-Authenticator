# ONDC-Authenticator
This is Main App use for ONDC Authentication Subscription and sending requests to BG or Gateway to perform operation on BPP(Seller App) by Buyer App (BAP)
Here's an updated `README.md` for your open-source GitHub project, now referring to ONDC Gateway/Registry APIs and including the environment endpoints in a table format:

Here’s a `README.md` file template for your ONDC Gateway project, including the details and structure you provided:

```markdown
# ONDC Gateway Integration

This repository provides a JavaScript implementation for integrating with the Open Network for Digital Commerce (ONDC) Gateway. It utilizes the Ed25519 signature scheme for authorization headers and communicates with ONDC services for search and lookup functionalities.

## Table of Contents
- [Features](#features)
- [Getting Started](#getting-started)
- [ONDC API Endpoints](#ondc-api-endpoints)
- [Authorization Header Generation](#authorization-header-generation)
- [Example Usage](#example-usage)
- [Contributing](#contributing)
- [License](#license)

## Features
- Generate BLAKE-512 digests for request bodies.
- Create authorization headers using Ed25519 signatures.
- Send POST requests to ONDC endpoints with proper authentication.

## Getting Started

### Prerequisites
Make sure you have [Node.js](https://nodejs.org/) installed. This project requires the following npm packages:
- `axios`
- `@noble/ed25519`
- `blakejs`

You can install the necessary packages using:

```bash
npm install axios @noble/ed25519 blakejs
```

### Environment Variables
Set up the following environment variables in your `.env` file or directly in your code:
- `SUBSCRIBER_ID`: Your ONDC subscriber ID.
- `UNIQUE_KEY_ID`: Your unique key ID for the ONDC.
- `PRIVATE_KEY`: Your Ed25519 private key for signing requests.

## ONDC API Endpoints

The following table summarizes the ONDC API endpoints for different environments:

| Environment      | Endpoint Type | URL                                      |
|------------------|---------------|------------------------------------------|
| **Staging**      | Gateway       | `https://staging.gateway.proteantech.in/search`  |
|                  | Registry      | `https://staging.registry.ondc.org/lookup`        |
|                  |               | `https://staging.registry.ondc.org/vlookup`       |
| **Pre-Production**| Gateway       | `https://preprod.gateway.ondc.org/search`         |
|                  | Registry      | `https://preprod.registry.ondc.org/ondc/lookup`  |
|                  |               | `https://preprod.registry.ondc.org/ondc/vlookup`  |
| **Production**   | Gateway       | `https://prod.gateway.ondc.org/search`            |
|                  | Registry      | `https://prod.registry.ondc.org/ondc/lookup`     |
|                  |               | `https://prod.registry.ondc.org/ondc/vlookup`     |

## Authorization Header Generation

To generate the Authorization header for your requests, follow these steps:

1. **Generate the digest** of the request body using the BLAKE-512 hashing function.
2. **Create Unix timestamps** for the `created` and `expires` fields.
3. **Concatenate** the `created`, `expires`, and `digest` into a signing string.
4. **Sign** the signing string using your Ed25519 private key.
5. **Generate** the base64 encoded string of the signature.
6. **Construct** the Authorization header.

### Example Request Body Structure
Use the following structure for your request body:

```json
{
  "context": {
    "domain": "nic2004:60212",
    "country": "IND",
    "city": "Kochi",
    "action": "search",
    "core_version": "0.9.1",
    "bap_id": "bap.stayhalo.in",
    "bap_uri": "https://your-bap-uri/",
    "transaction_id": "your-transaction-id",
    "message_id": "your-message-id",
    "timestamp": "your-timestamp",
    "ttl": "P1M"
  },
  "message": {
    "intent": {
      "fulfillment": {
        "start": {
          "location": {
            "gps": "10.108768, 76.347517"
          }
        },
        "end": {
          "location": {
            "gps": "10.102997, 76.353480"
          }
        }
      }
    }
  }
}
```

## Example Usage

Below is a basic example of how to use the ONDC Gateway integration in your project:

```javascript
(async () => {
  const url = 'https://staging.gateway.proteantech.in/search';
  const subscriberId = 'example-bap.com';
  const uniqueKeyId = 'bap1234';
  const privateKey = 'your-private-key-here';
  
  // Define your request body here
  const requestBody = {
    // Your request body goes here
  };

  try {
    const response = await sendPostRequestWithAuth(url, subscriberId, uniqueKeyId, privateKey, requestBody);
    console.log('Response:', response);
  } catch (error) {
    console.error('Error:', error);
  }
})();
```

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License
This project is open-source and available under the [MIT License](LICENSE).
```

### Customization:
- Replace `"your-private-key-here"` in the example usage section with instructions on how to set the private key securely.
- Feel free to modify any section to better fit your project's specifics.
- Ensure the table for endpoints is correctly formatted, and the URLs are accurate.

Let me know if you need any additional changes!
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

This `README.md` should provide all necessary details for users of your open-source project on GitHub!
