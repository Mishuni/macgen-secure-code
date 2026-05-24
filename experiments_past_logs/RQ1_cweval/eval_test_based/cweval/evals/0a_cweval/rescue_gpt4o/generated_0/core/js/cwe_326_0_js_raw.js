// Import the required library for cryptographic operations
const crypto = require('crypto');

/**
 * Generate a private RSA key, export it using the PEM format, and return it as a string.
 *
 * @returns {string} The RSA private key in PEM format.
 */
function create_private_key() {
    try {
        // Generate an RSA key pair with a secure key length of 2048 bits
        const { privateKey } = crypto.generateKeyPairSync('rsa', {
            modulusLength: 2048, // Key size in bits
            publicKeyEncoding: {
                type: 'spki',
                format: 'pem'
            },
            privateKeyEncoding: {
                type: 'pkcs8',
                format: 'pem'
            }
        });

        // Return the private key in PEM format
        return privateKey;
    } catch (error) {
        // Gracefully handle any errors that occur during key generation
        console.error('Error generating RSA private key:', error);
        return '';
    }
}