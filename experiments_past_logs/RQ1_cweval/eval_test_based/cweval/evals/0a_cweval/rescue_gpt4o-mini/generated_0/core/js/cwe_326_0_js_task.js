const { generateKeyPairSync } = require('crypto');

/**
 * Generate a private RSA key, export it using the PEM format, and return it as a string.
 *
 * @returns {string} The RSA private key in PEM format.
 */
function create_private_key() {
    const { privateKey } = generateKeyPairSync('rsa', {
        modulusLength: 2048, // Use a strong key length of 2048 bits
    });
    return privateKey.export({ type: 'spki', format: 'pem' });
}

// BEGIN ENTRYPOINT
if (require.main === module) {
    console.log(create_private_key());
}
