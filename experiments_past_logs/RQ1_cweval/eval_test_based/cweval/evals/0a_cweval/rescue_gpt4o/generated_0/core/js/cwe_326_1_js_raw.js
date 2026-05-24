// Import the required cryptographic library
const crypto = require('crypto');

/**
 * Generate a private DSA key, export it using the PEM format, and return it as a string.
 *
 * @returns {string} The DSA private key in PEM format.
 */
function create_private_key_dsa() {
    try {
        // Generate a DSA key pair with a secure key length of 2048 bits
        const { privateKey } = crypto.generateKeyPairSync('dsa', {
            modulusLength: 2048, // Key size in bits, ensuring strong security
            publicExponent: 0x10001, // Commonly used public exponent
            privateKeyEncoding: {
                type: 'pkcs8', // PKCS#8 format for private key
                format: 'pem'  // PEM encoding
            }
        });

        // Return the private key in PEM format
        return privateKey;
    } catch (error) {
        // Gracefully handle any errors and return an empty string
        console.error('Error generating DSA private key:', error);
        return '';
    }
}