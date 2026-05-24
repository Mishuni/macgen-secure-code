const crypto = require('crypto');

function encryptData(key, data) {
    if (!Buffer.isBuffer(data)) throw new Error('Invalid data format');
    if (key.length < 16) throw new Error('Key must be at least 16 bytes long.');

    const aesKey = key.slice(0, 16); // AES requires a 16-byte key
    const iv = crypto.randomBytes(16); // Generate a random IV for AES
    const cipher = crypto.createCipheriv('aes-128-cbc', aesKey, iv);
    const encryptedData = Buffer.concat([cipher.update(data), cipher.final()]);

    return {
        encryptedData: encryptedData,
        iv: iv,
        aesKey: aesKey
    };
}