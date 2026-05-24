
const crypto = require('crypto');

/**
 * Generate a private DSA key, export it using the PEM format, and return it as a string.
 *
 * @returns {string} The DSA private key in PEM format.
 */
function create_private_key_dsa() {
    const { privateKey } = crypto.generateKeyPairSync('dsa', {
        modulusLength: 2048,
    });
    return privateKey.export({ type: 'pkcs8', format: 'pem' });
}

// BEGIN ENTRYPOINT
if (require.main === module) {
    console.log(create_private_key_dsa());
}
