
const crypto = require('crypto');

/**
 * Hash the given certificate securely and return the hash as a hexadecimal string.
 *
 * @param {string} cert - The certificate to be hashed.
 * @returns {string} The securely hashed certificate as a hexadecimal string.
 * @throws {Error} If the input is not a non-empty string.
 */
function hash_certificate(cert) {
    // Input validation
    if (typeof cert !== 'string' || cert.trim() === '') {
        throw new Error('Input must be a non-empty string.');
    }

    // Create a secure hash of the certificate
    const hash = crypto.createHash('sha256');
    hash.update(cert);

    // Return the hash as a hexadecimal string
    return hash.digest('hex');
}