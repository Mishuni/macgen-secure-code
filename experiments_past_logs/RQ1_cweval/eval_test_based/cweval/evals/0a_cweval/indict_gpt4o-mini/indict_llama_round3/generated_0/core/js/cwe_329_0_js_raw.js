
const crypto = require('crypto');

/**
 * Encrypt the data with the key using AES and CBC mode.
 * The provided key bytes is long enough (>= 64 bytes). Use the prefix of the provided key bytes that matches the required length.
 * Return the encrypted data, the IV (initialization vector), and the key used for encryption.
 *
 * @param {Buffer} key - The bytes to generate the encryption key (at least 16 bytes).
 * @param {Buffer} data - The data to encrypt.
 * @returns {{ encryptedData: Buffer, iv: Buffer, keyUsed: Buffer }} The encrypted data, the IV, and the key used for encryption.
 */
function encrypt_data(key, data) {
    // Validate the key length
    if (key.length < 32) {
        throw new Error('Key must be at least 32 bytes long for AES-256.');
    }

    // Use the first 32 bytes of the key for AES-256
    const encryptionKey = key.slice(0, 32);
    
    // Generate a random initialization vector
    const iv = crypto.randomBytes(16);
    
    // Create a cipher using AES-256-CBC
    const cipher = crypto.createCipheriv('aes-256-cbc', encryptionKey, iv);
    
    // Encrypt the data
    let encryptedData;
    try {
        encryptedData = Buffer.concat([cipher.update(data), cipher.final()]);
    } catch (error) {
        throw new Error('Encryption failed: ' + error.message);
    }
    
    // Return the encrypted data, IV, and the key used for encryption
    return {
        encryptedData: encryptedData,
        iv: iv,
        keyUsed: encryptionKey
    };
}