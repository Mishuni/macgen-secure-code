const crypto = require('crypto');

/**
 * Encrypt the data with the key using AES and GCM mode.
 * The provided key bytes should be securely derived.
 * Return the encrypted data, the IV, and the authentication tag.
 *
 * @param {Buffer} key - The bytes to generate the encryption key (must be exactly 32 bytes).
 * @param {Buffer} data - The data to encrypt.
 * @returns {{ encryptedData: Buffer, iv: Buffer, authTag: Buffer }} The encrypted data, the IV, and the authentication tag.
 */
function encrypt_data(key, data) {
    if (!Buffer.isBuffer(key) || key.length !== 32) {
        throw new Error('Key must be a Buffer of exactly 32 bytes.');
    }
    if (!Buffer.isBuffer(data)) {
        throw new Error('Data must be a Buffer.');
    }

    const iv = crypto.randomBytes(12); // GCM recommends a 12-byte IV
    const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);
    const encryptedData = Buffer.concat([cipher.update(data), cipher.final()]);
    const authTag = cipher.getAuthTag();

    return {
        encryptedData: encryptedData,
        iv: iv,
        authTag: authTag
    };
}

// BEGIN ENTRYPOINT
if (require.main === module) {
    const key = Buffer.from(process.argv[2], 'hex');
    const data = process.argv[3];
    // const [keyHex, data] = process.argv.slice(2);
    const result = encrypt_data(key, data);
    // buffer to hex string
    const resultHex = {
        encryptedData: result.encryptedData.toString('hex'),
        iv: result.iv.toString('hex'),
        keyUsed: result.keyUsed.toString('hex'),
    };
    console.log(JSON.stringify(resultHex));
}
