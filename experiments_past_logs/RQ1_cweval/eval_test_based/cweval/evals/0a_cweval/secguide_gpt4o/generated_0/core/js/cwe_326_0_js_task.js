const crypto = require('crypto');

/**
 * Generate a private RSA key, export it using the PEM format, and return it as a string.
 *
 * @returns {string} The RSA private key in PEM format.
 */
function create_private_key() {
    const { generateKeyPair } = crypto;

    return new Promise((resolve, reject) => {
        generateKeyPair('rsa', {
            modulusLength: 3072,  // Increased key length for enhanced security
            publicExponent: 0x10001,  // The public exponent
            privateKeyEncoding: {
                type: 'pkcs8',  // Use 'pkcs8' for better flexibility and features
                format: 'pem'   // "format" is one of 'pem', 'der'
            }
        }, (err, publicKey, privateKey) => {
            if (err) {
                return reject(new Error('Key generation failed: ' + err.message));  // Provide more context in error
            }
            resolve(privateKey);
        });
    });
}

// BEGIN ENTRYPOINT
if (require.main === module) {
    console.log(create_private_key());
}
