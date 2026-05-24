
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
    if (!Buffer.isBuffer(key) || !Buffer.isBuffer(data)) {
        throw new Error('Key and data must be Buffers');
    }

    // AES requires a key length of 32 bytes (256 bits) for AES-256
    const aesKey = key.slice(0, 32);
    const iv = crypto.randomBytes(16); // AES block size is 16 bytes

    const cipher = crypto.createCipheriv('aes-256-cbc', aesKey, iv);
    let encryptedData;
    
    try {
        encryptedData = cipher.update(data, 'utf8', 'hex');
        encryptedData += cipher.final('hex');
    } catch (error) {
        throw new Error('Encryption failed: ' + error.message);
    }

    // Do not expose the key in the output for security reasons
    return {
        encryptedData: encryptedData,
        iv: iv.toString('hex'),
        aesKey: aesKey.toString('hex') // Consider removing this in production
    };
}