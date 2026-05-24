
const crypto = require('crypto');

/**
 * Encrypt the data with the key using GCM mode.
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
    const aesKey = key.slice(0, 32); // Use the first 32 bytes for AES
    const iv = crypto.randomBytes(12); // GCM mode requires a 12-byte IV
    const cipher = crypto.createCipheriv('aes-256-gcm', aesKey, iv);
    
    const encryptedData = Buffer.concat([cipher.update(data), cipher.final()]);
    const tag = cipher.getAuthTag(); // Get the authentication tag

    return {
        encryptedData: Buffer.concat([encryptedData, tag]), // Include the tag with the encrypted data
        iv: iv,
        aesKey: aesKey
    };
}