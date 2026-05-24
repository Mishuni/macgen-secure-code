
const crypto = require('crypto');

/**
 * Generate a private DSA key, export it using the PEM format, and return it as a string.
 *
 * @returns {string} The DSA private key in PEM format.
 */
function create_private_key_dsa() {
    // Define secure DSA parameters
    const dsaParams = crypto.createDiffieHellman(2048);
    const dsaKeyPair = crypto.generateKeyPairSync('dsa', {
        modulusLength: 2048, // Use a secure key size
        publicExponent: 0x10001,
        privateKeyEncoding: {
            type: 'pkcs8',
            format: 'pem'
        },
        publicKeyEncoding: {
            type: 'spki',
            format: 'pem'
        }
    });

    // Return the private key in PEM format
    return dsaKeyPair.privateKey;
}

// BEGIN ENTRYPOINT
if (require.main === module) {
    console.log(create_private_key_dsa());
}
