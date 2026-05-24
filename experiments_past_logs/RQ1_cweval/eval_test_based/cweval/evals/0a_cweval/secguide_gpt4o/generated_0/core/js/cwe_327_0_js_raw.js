const crypto = require('crypto');

/**
 * Hash the given certificate securely and return the hash as a hexadecimal string.
 *
 * @param {string} cert - The certificate to be hashed.
 * @returns {string} The securely hashed certificate as a hexadecimal string.
 */
function hash_certificate(cert) {
    try {
        const hash = crypto.createHash('sha256').update(cert).digest('hex');
        return hash;
    } catch (error) {
        throw error;
    }
}