const crypto = require('crypto');

/**
 * Hash the given certificate securely and return the hash as a hexadecimal string.
 *
 * @param {string} cert - The certificate to be hashed.
 * @returns {string} The securely hashed certificate as a hexadecimal string.
 */
function hash_certificate(cert) {
    if (typeof cert !== 'string' || cert.length === 0) {
        throw new Error('Invalid certificate');
    }
    if (cert.length > 2048) {
        throw new Error('Certificate too long');
    }
    
    const hash = crypto.createHash('sha512');
    hash.update(cert);
    return hash.digest('hex');
}