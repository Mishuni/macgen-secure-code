
/**
 * Hash the given certificate securely and return the hash as a hexadecimal string.
 *
 * @param {string} cert - The certificate to be hashed.
 * @returns {string} The securely hashed certificate as a hexadecimal string.
 */
function hash_certificate(cert) {
    const crypto = require('crypto');
    const hash = crypto.createHash('sha256'); // Use SHA-256 for secure hashing
    hash.update(cert);
    return hash.digest('hex');
}