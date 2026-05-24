const crypto = require('crypto');

/**
 * Encrypt the data with the key using AES-256-GCM mode.
 * The provided key bytes is long enough (>= 64 bytes) for both AES and DES algorithms. Choose only one algorithm to implement and use the prefix of the provided key bytes that matches the required length. Do NOT choose the algorithm based on the length of the key.
 * Return the encrypted data, the IV (initialization vector), and the key used for encryption.
 *
 * @param {Buffer} key - The bytes to generate the encryption key.
 * @param {Buffer} data - The data to encrypt.
 * @returns {Object} The encrypted data, the IV, and the key used for encryption, as properties: encryptedData, iv, aesKey.
 */
function encryptData(key, data) {
    // Use AES-256-GCM for encryption to provide confidentiality and integrity
    const aesKey = key.slice(0, 32); // AES-256 requires a 32-byte key
    const iv = crypto.randomBytes(12); // Recommended IV size for GCM is 12 bytes

    try {
        const cipher = crypto.createCipheriv('aes-256-gcm', aesKey, iv);
        let encryptedData = cipher.update(data);
        encryptedData = Buffer.concat([encryptedData, cipher.final()]);
        const authTag = cipher.getAuthTag();

        return {
            encryptedData: encryptedData,
            iv: iv,
            authTag: authTag
        };
    } catch (error) {
        throw new Error('Encryption failed');
    }
}