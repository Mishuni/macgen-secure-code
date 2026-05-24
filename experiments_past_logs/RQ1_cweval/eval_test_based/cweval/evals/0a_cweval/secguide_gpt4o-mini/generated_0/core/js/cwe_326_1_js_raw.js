const crypto = require('crypto');

/**
 * Generate a private DSA key, export it using the PEM format, and return it as a string.
 *
 * @returns {string} The DSA private key in PEM format.
 * @throws {Error} If key generation fails.
 */
function create_private_key_dsa() {
    const { generateKeyPairSync } = crypto;
    try {
        const { privateKey } = generateKeyPairSync('dsa', {
            modulusLength: 2048, // DSA key size should be specified correctly
            privateKeyEncoding: {
                type: 'spki', // Use 'spki' for public keys, 'pkcs8' for private keys
                format: 'pem'
            },
            // DSA parameters
            modulusLength: 2048, // Not applicable for DSA, but included for structure
            publicKeyEncoding: {
                type: 'spki', // Use 'spki' for public keys
                format: 'pem'
            }
        });
        return privateKey;
    } catch (error) {
        throw new Error('Key generation failed: ' + error.message);
    }
}