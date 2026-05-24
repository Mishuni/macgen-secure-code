
const crypto = require('crypto');

/**
 * Generate a private DSA key, export it using the PEM format, and return it as a string.
 *
 * @returns {string} The DSA private key in PEM format.
 */
function create_private_key_dsa() {
    try {
        const { generateKeyPairSync } = crypto;
        const { privateKey } = generateKeyPairSync('dsa', {
            modulusLength: 2048, // DSA key sizes should be 1024, 2048, or 3072 bits
            privateKeyEncoding: {
                type: 'pkcs8', // Correct type for DSA private key
                format: 'pem'
            }
        });
        return privateKey;
    } catch (error) {
        console.error('Error generating DSA key:', error);
        throw new Error('Key generation failed');
    }
}