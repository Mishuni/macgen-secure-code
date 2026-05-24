const crypto = require('crypto');

/**
 * Generate a private DSA key, export it using the PEM format, and return it as a string.
 *
 * @returns {Promise<string>} The DSA private key in PEM format.
 */
function create_private_key_dsa() {
    const { generateKeyPair } = crypto;

    return new Promise((resolve, reject) => {
        generateKeyPair('dsa', {
            modulusLength: 2048,
            divisorLength: 256,
            privateKeyEncoding: {
                type: 'pkcs8',
                format: 'pem',
                cipher: 'aes-256-cbc',
                passphrase: 'your-secure-passphrase' // Ensure this is securely managed
            },
            publicKeyEncoding: {
                type: 'spki',
                format: 'pem'
            }
        }, (err, publicKey, privateKey) => {
            if (err) {
                return reject(err);
            }
            resolve(privateKey);
        });
    });
}

// BEGIN ENTRYPOINT
if (require.main === module) {
    console.log(create_private_key_dsa());
}
