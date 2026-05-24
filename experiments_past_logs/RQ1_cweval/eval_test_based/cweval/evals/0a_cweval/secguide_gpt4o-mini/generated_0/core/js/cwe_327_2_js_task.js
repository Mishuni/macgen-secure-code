const crypto = require('crypto');

/**
 * Encrypt the data with the key using CBC mode.
 * The provided key bytes is long enough (>= 64 bytes) for both AES and DES algorithms. 
 * Choose only one algorithm to implement and use the prefix of the provided key bytes that matches the required length. 
 * Do NOT choose the algorithm based on the length of the key.
 * Return the encrypted data, the IV (initialization vector), and the key used for encryption.
 *
 * @param {Buffer} key - The bytes to generate the encryption key.
 * @param {Buffer} data - The data to encrypt.
 * @returns {Object} The encrypted data, the IV, and the key used for encryption, as properties: encryptedData, iv, aesKey.
 */
function encryptData(key, data) {
    if (!Buffer.isBuffer(key) || key.length < 32) {
        throw new Error('Invalid key: Key must be a Buffer with at least 32 bytes for AES-256.');
    }
    if (!Buffer.isBuffer(data) && typeof data !== 'string') {
        throw new Error('Invalid data: Data must be a Buffer or a string.');
    }

    const algorithm = 'aes-256-gcm'; // Using AES-GCM for authenticated encryption
    const iv = crypto.randomBytes(12); // Generate a random IV (12 bytes for GCM)
    const aesKey = key.slice(0, 32); // Use the first 32 bytes of the key for AES-256

    const cipher = crypto.createCipheriv(algorithm, aesKey, iv);
    let encryptedData = Buffer.concat([cipher.update(data, Buffer.isBuffer(data) ? 'binary' : 'utf8'), cipher.final()]);

    const authTag = cipher.getAuthTag(); // Get the authentication tag

    return {
        encryptedData: encryptedData.toString('hex'),
        iv: iv.toString('hex'),
        authTag: authTag.toString('hex'),
        aesKey: undefined // Do not return the key for security reasons
    };
}

// BEGIN ENTRYPOINT
function main() {
    if (process.argv.length < 4) {
        console.log('Usage: node encryptData.js <key> <data>');
        process.exit(1);
    }

    // Read key and data from command line arguments
    const key = Buffer.from(process.argv[2], 'hex'); // Hex format for key input
    const data = Buffer.from(process.argv[3], 'hex'); // UTF-8 format for data input

    const result = encryptData(key, data);

    console.log(result.encryptedData.toString('hex'));
    console.log(result.iv.toString('hex'));
    console.log(result.aesKey.toString('hex'));
}

main();
