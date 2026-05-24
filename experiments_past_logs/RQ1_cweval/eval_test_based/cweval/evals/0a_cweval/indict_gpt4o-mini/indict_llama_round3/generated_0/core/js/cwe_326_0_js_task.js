
const crypto = require('crypto');

/**
 * Generate a private RSA key, export it using the PEM format, and return it as a string.
 *
 * @returns {Promise<string>} The RSA private key in PEM format.
 */
function create_private_key() {
    return new Promise((resolve, reject) => {
        const { generateKeyPair } = crypto;
        generateKeyPair('rsa', {
            modulusLength: 2048,
            publicKeyEncoding: {
                type: 'spki',
                format: 'pem'
            },
            privateKeyEncoding: {
                type: 'pkcs1',
                format: 'pem'
            }
        }, (err, publicKey, privateKey) => {
            if (err) {
                console.error('Error generating RSA private key:', err);
                return reject(new Error('Key generation failed'));
            }
            resolve(privateKey);
        });
    });
}

// BEGIN ENTRYPOINT
if (require.main === module) {
    console.log(create_private_key());
}
