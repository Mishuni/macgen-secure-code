const crypto = require('crypto');

/**
 * Encrypt the data with the key using AES and GCM mode.
 * The provided key bytes is long enough (>= 64 bytes). Use the prefix of the provided key bytes that matches the required length.
 * Return the encrypted data, the IV (initialization vector), and the authentication tag.
 *
 * @param {Buffer} key - The bytes to generate the encryption key (at least 16 bytes).
 * @param {Buffer} data - The data to encrypt.
 * @returns {{ encryptedData: Buffer, iv: Buffer, authTag: Buffer }} The encrypted data, the IV, and the authentication tag.
 */
function encrypt_data(key, data) {
    // Ensure the key is at least 16 bytes long
    const keyLength = 16;
    if (key.length < keyLength) {
        throw new Error('Key must be at least 16 bytes long');
    }
    const keyUsed = key.slice(0, keyLength);

    // Generate a random Initialization Vector (IV)
    const iv = crypto.randomBytes(12); // 12 bytes is recommended for GCM

    // Create a Cipher instance using AES-128-GCM
    const cipher = crypto.createCipheriv('aes-128-gcm', keyUsed, iv);

    // Encrypt the data
    let encryptedData = cipher.update(data);
    encryptedData = Buffer.concat([encryptedData, cipher.final()]);

    // Get the authentication tag
    const authTag = cipher.getAuthTag();

    return {
        encryptedData: encryptedData,
        iv: iv,
        authTag: authTag
    };
}