// ondcRequest.js

const blake = require('blakejs');
const nacl = require('tweetnacl');
const base64url = require('base64url');
const { v4: uuidv4 } = require('uuid');
const fetch = require('node-fetch');
const { TextEncoder } = require('util');
const fs = require('fs');
const path = require('path');
const createCsvWriter = require('csv-writer').createObjectCsvWriter;

/**
 * Hashes the message using BLAKE-512 and returns a base64-encoded string.
 * 
 * @param {string} msg - The message to hash.
 * @returns {string} - The base64-encoded hash.
 */
function hashMessage(msg) {
    const hash = blake.blake2b(msg, null, 64); // BLAKE-512 outputs 64 bytes
    const hashBase64 = Buffer.from(hash).toString('base64');
    return hashBase64;
}

/**
 * Creates the signing string using created, expires, and digest.
 * 
 * @param {string} digestBase64 - The base64-encoded digest.
 * @param {number} created - The creation timestamp (Unix time).
 * @param {number} expires - The expiration timestamp (Unix time).
 * @returns {string} - The signing string.
 */
function createSigningString(digestBase64, created, expires) {
    return `(created): ${created}\n(expires): ${expires}\ndigest: BLAKE-512=${digestBase64}`;
}

/**
 * Signs the signing string using the Ed25519 private key.
 * 
 * @param {string} signingString - The string to sign.
 * @param {string} privateKeyBase64 - The base64-encoded Ed25519 private key (64 bytes).
 * @returns {string} - The base64-encoded signature.
 */
function signResponse(signingString, privateKeyBase64) {
    // Decode the private key from base64
    const privateKeyBytes = Buffer.from(privateKeyBase64, 'base64');

    if (privateKeyBytes.length !== 64) {
        throw new Error('Invalid private key length. Expected 64 bytes for Ed25519.');
    }

    // Initialize TextEncoder
    const encoder = new TextEncoder();

    // Encode the signing string as Uint8Array
    const signingStringUint8 = encoder.encode(signingString);

    // Sign the signing string
    const signature = nacl.sign.detached(signingStringUint8, privateKeyBytes);

    // Return base64-encoded signature
    return Buffer.from(signature).toString('base64');
}

/**
 * Creates the Authorization header based on the request body and keys.
 * 
 * @param {Object} requestBody - The JSON request body.
 * @param {string} privateKey - The base64-encoded Ed25519 private key.
 * @param {string} subscriberId - The subscriber ID.
 * @param {string} uniqueKeyId - The unique key ID.
 * @returns {string} - The Authorization header.
 */
function createAuthorizationHeader(requestBody, privateKey, subscriberId, uniqueKeyId) {
    // Hash the request body
    const jsonString = JSON.stringify(requestBody, separators = [',', ':']);
    const digestBase64 = hashMessage(jsonString);

    // Generate created and expires timestamps
    const created = Math.floor(Date.now() / 1000); // Current Unix timestamp in seconds
    const expires = created + 3600; // Expires in 1 hour

    // Create signing string
    const signingString = createSigningString(digestBase64, created, expires);

    // Sign the signing string
    const signature = signResponse(signingString, privateKey);

    // Construct the Authorization header
    const authorizationHeader = `Signature keyId="${subscriberId}|${uniqueKeyId}|ed25519",` +
        `algorithm="ed25519",` +
        `created="${created}",` +
        `expires="${expires}",` +
        `headers="(created) (expires) digest",` +
        `signature="${signature}"`;

    return authorizationHeader;
}

/**
 * Saves the transaction details to transactions.csv
 * 
 * @param {Object} data - Transaction data.
 * @param {string} data.transaction_id - The transaction ID.
 * @param {string} data.message_id - The message ID.
 * @param {string} data.timestamp - The timestamp in ISO format.
 */
async function saveTransactionData({ transaction_id, message_id, timestamp }) {
    const transactionsCsvPath = path.join(__dirname, 'transactions.csv');

    // Check if transactions.csv exists
    const transactionsFileExists = fs.existsSync(transactionsCsvPath);

    // Create CSV writer
    const csvWriter = createCsvWriter({
        path: transactionsCsvPath,
        header: [
            { id: 'transaction_id', title: 'Transaction ID' },
            { id: 'message_id', title: 'Message ID' },
            { id: 'timestamp', title: 'Timestamp' }
        ],
        append: transactionsFileExists // Append if file exists, else create with headers
    });

    // Write data
    await csvWriter.writeRecords([
        { transaction_id, message_id, timestamp }
    ]);
}

/**
 * Saves the request and response data to requests_responses.csv
 * 
 * @param {Object} data - Request and response data.
 * @param {string} data.transaction_id - The transaction ID.
 * @param {Object} data.requestBody - The request body JSON.
 * @param {Object} data.responseData - The response data JSON.
 */
async function saveRequestResponse({ transaction_id, requestBody, responseData }) {
    const rrCsvPath = path.join(__dirname, 'requests_responses.csv');

    // Check if requests_responses.csv exists
    const rrFileExists = fs.existsSync(rrCsvPath);

    // Create CSV writer
    const csvWriter = createCsvWriter({
        path: rrCsvPath,
        header: [
            { id: 'transaction_id', title: 'Transaction ID' },
            { id: 'request', title: 'Request JSON' },
            { id: 'response', title: 'Response JSON' }
        ],
        append: rrFileExists // Append if file exists, else create with headers
    });

    // Prepare data by stringifying JSON objects
    const requestString = JSON.stringify(requestBody);
    const responseString = responseData ? JSON.stringify(responseData) : '';

    // Write data
    await csvWriter.writeRecords([
        { transaction_id, request: requestString, response: responseString }
    ]);
}

/**
 * Sends an ONDC request with a properly constructed Authorization header.
 * 
 * @param {Object} params - Parameters for the request.
 * @param {string} params.stagingUrl - The ONDC Staging URL to send the request to.
 * @param {string} params.subscriberId - The subscriber ID (e.g., "example-bap.com").
 * @param {string} params.uniqueKeyId - The unique key ID assigned to the subscriber.
 * @param {string} params.privateKey - The base64-encoded Ed25519 private key (64 bytes, base64-encoded).
 */
async function sendOndcRequest({ stagingUrl, subscriberId, uniqueKeyId, privateKey }) {
    // Generate dynamic fields
    const created = Math.floor(Date.now() / 1000); // Current Unix timestamp in seconds
    const expires = created + 3600; // Expires in 1 hour
    const message_id = uuidv4();
    const transaction_id = uuidv4();

    // Construct the request body with dynamic fields and embedded messageContent
    const requestBody = {
        context: {
            domain: "nic2004:60212",
            country: "IND",
            city: "Kochi",
            action: "search",
            core_version: "0.9.1",
            bap_id: subscriberId,
            bap_uri: stagingUrl, // Adjust based on your actual URI if necessary
            transaction_id: transaction_id,
            message_id: message_id,
            timestamp: new Date(created * 1000).toISOString(),
            ttl: "P1M"
        },
        message: {
            intent: {
                fulfillment: {
                    start: {
                        location: {
                            gps: "10.108768, 76.347517"
                        }
                    },
                    end: {
                        location: {
                            gps: "10.102997, 76.353480"
                        }
                    }
                }
            }
        }
    };

    // Create Authorization header
    let authorizationHeader;
    try {
        authorizationHeader = createAuthorizationHeader(requestBody, privateKey, subscriberId, uniqueKeyId);
    } catch (error) {
        console.error('Error creating Authorization header:', error.message);
        return;
    }

    console.log('Authorization Header:', authorizationHeader);

    // Prepare the HTTP request options
    const requestOptions = {
        method: 'POST', // Change to 'GET', 'PUT', etc., as needed
        headers: {
            'Content-Type': 'application/json',
            'Authorization': authorizationHeader
        },
        body: JSON.stringify(requestBody)
    };

    // Send the HTTP request
    let responseData = null;
    let responseStatus = null;
    try {
        const response = await fetch(stagingUrl, requestOptions);
        responseStatus = response.status;
        responseData = await response.json();

        console.log('Response Status:', response.status);
        console.log('Response Body:', JSON.stringify(responseData, null, 2));
    } catch (error) {
        console.error('Error sending the request:', error.message);
    }

    // Save transaction details and request/response to CSV
    try {
        await saveTransactionData({
            transaction_id,
            message_id,
            timestamp: requestBody.context.timestamp
        });

        await saveRequestResponse({
            transaction_id,
            requestBody,
            responseData
        });

        console.log('Data successfully saved to CSV files.');
    } catch (error) {
        console.error('Error saving data to CSV:', error.message);
    }
}

// Example usage:
(async () => {
    // Replace the following values with your actual data
    const stagingUrl = 'https://ondc-staging.example.com/api'; // Replace with your ONDC Staging URL
    const subscriberId = 'example-bap.com'; // Your subscriber ID
    const uniqueKeyId = 'bap1234'; // Your unique key ID
    const privateKey = 'lP3sHA+9gileOkXYJXh4Jg8tK0gEEMbf9yCPnFpbldhrAY+NErqL9WD+Vav7TE5tyVXGXBle9ONZi2W7o144eQ=='; // Your base64-encoded Ed25519 private key

    // Call the function to send the request
    await sendOndcRequest({
        stagingUrl,
        subscriberId,
        uniqueKeyId,
        privateKey
    });
})();
