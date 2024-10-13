Here’s a README file for your project, detailing the functionality and usage of the provided code.

```markdown
# API Request Logger

This project is a Python script designed to send authenticated API requests, log request and response details, and save this information in CSV and log file formats. The script uses the NaCl library for cryptographic signing and the `requests` library to handle HTTP requests.

## Features

- Generate unique transaction and message IDs.
- Create a secure authorization header using private key signing.
- Send JSON body as part of the request.
- Log all request and response details, including:
  - Request body
  - Created and expiration timestamps
  - Response status code and body
- Append data to existing CSV and log files without overwriting.

## Prerequisites

- Python 3.x
- Required Python packages:
  - `nacl`
  - `requests`

You can install the necessary packages using pip:

```bash
pip install pynacl requests
```

## Usage

1. Clone the repository or download the script.

2. Update the hard-coded values in the script:
   - Replace `YOUR_SUBSCRIBER_ID` with your actual subscriber ID.
   - Replace `Your_UNIQUE_KEY_ID` with your unique key ID.
   - Replace `YOUR_PRIVATE_KEY` with your private key.
   - Update the `url` variable with the desired API endpoint.

3. Run the script:

```bash
python your_script_name.py
```

## Code Overview

- **Hashing and Signing**:
  - The script uses the Blake2b hashing algorithm to hash the message and then signs the hash with an Ed25519 private key.
  
- **Authorization Header Creation**:
  - Generates an authorization header for API requests using the created timestamp, expiration timestamp, and the signed hash.

- **Logging Functionality**:
  - The `log_request_response` function saves the request body, timestamps, IDs, and response details into a CSV file (`request_log.csv`) and a log file (`request_response.log`).
  - Each entry is timestamped and appended to the existing files if they already exist.

## File Structure

- `request_log.csv` - CSV file that logs request and response data.
- `request_response.log` - Log file that contains a detailed request-response log.

## Contributing

Feel free to fork the repository and submit pull requests. If you have suggestions for improvements or find bugs, please create an issue in the GitHub repository.

## License

This project is open-source and available under the [MIT License](LICENSE).

```

### Instructions for Use

1. **Make sure to update the values in the code** to reflect your actual API credentials and endpoint before running it.
2. **Install the required libraries** as mentioned in the prerequisites section.
3. **Run the script** to initiate the API request and log the details. The CSV and log files will be created or appended to as necessary. 

Feel free to modify any sections based on your specific needs or additional features you might want to highlight!
