const crypto = require('crypto');

/**
 * Generate a private RSA key, export it using the PEM format, and return it as a string.
 *
 * @returns {string} The RSA private key in PEM format.
 */
function create_private_key() {
    const { generateKeyPair } = crypto;
    const passphrase = process.env.PRIVATE_KEY_PASSPHRASE; // Use an environment variable for the passphrase

    return new Promise((resolve, reject) => {
        if (!passphrase) {
            return reject(new Error('Passphrase is not set in the environment variables.'));
        }

        generateKeyPair('rsa', {
            modulusLength: 4096, // Recommended key length for better security
            publicKeyEncoding: {
                type: 'spki',
                format: 'pem'
            },
            privateKeyEncoding: {
                type: 'pkcs8',
                format: 'pem',
                cipher: 'aes-256-gcm', // Use GCM mode for authenticated encryption
                passphrase: passphrase // Use the secure passphrase from environment variable
            }
        }, (err, publicKey, privateKey) => {
            if (err) {
                return reject(new Error(`Key generation failed: ${err.message}`)); // Provide more context in the error
            }
            resolve(privateKey); // Return the encrypted private key
        });
    });
}