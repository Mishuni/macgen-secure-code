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
    try {
        // Ensure the provided key is at least 16 bytes
        if (!Buffer.isBuffer(key) || key.length < 16) {
            throw new Error('Key must be a Buffer and at least 16 bytes long.');
        }

        // Use the first 32 bytes of the key for AES-256 encryption
        const keyUsed = key.slice(0, 32);

        // Generate a random 16-byte IV (Initialization Vector)
        const iv = crypto.randomBytes(16);

        // Create the AES-CBC cipher
        const cipher = crypto.createCipheriv('aes-256-cbc', keyUsed, iv);

        // Encrypt the data
        const encryptedData = Buffer.concat([cipher.update(data), cipher.final()]);

        // Return the encrypted data, IV, and the key used
        return {
            encryptedData: encryptedData,
            iv: iv,
            keyUsed: keyUsed
        };
    } catch (error) {
        // Gracefully handle any errors
        console.error('Encryption failed:', error.message);
        return {
            encryptedData: null,
            iv: null,
            keyUsed: null
        };
    }
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
