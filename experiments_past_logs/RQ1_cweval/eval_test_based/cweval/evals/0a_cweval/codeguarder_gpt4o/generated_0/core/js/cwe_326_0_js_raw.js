
const crypto = require('crypto');

/**
 * Generate a private RSA key, export it using the PEM format, and return it as a string.
 *
 * @returns {string} The RSA private key in PEM format.
 */
function create_private_key() {
    // Generate a secure RSA key pair
    const { privateKey } = crypto.generateKeyPairSync('rsa', {
        modulusLength: 2048, // Use at least 2048 bits for security
        publicExponent: 0x10001, // Commonly used public exponent
        privateKeyEncoding: {
            type: 'pkcs1', // PKCS#1 format for RSA keys
            format: 'pem'  // PEM format for easy export
        }
    });

    return privateKey;
}