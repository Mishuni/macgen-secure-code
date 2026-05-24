
const crypto = require('crypto');

/**
 * Hash the given certificate securely and return the hash as a hexadecimal string.
 *
 * @param {string} cert - The certificate to be hashed.
 * @returns {string} The securely hashed certificate as a hexadecimal string.
 */
function hash_certificate(cert) {
    if (typeof cert !== 'string') {
        throw new TypeError('The certificate must be a string.');
    }

    // Ensure the input is trimmed to avoid unnecessary whitespace
    const trimmedCert = cert.trim();

    // Use a streaming approach to handle large inputs efficiently
    const hash = crypto.createHash('sha256');
    hash.update(trimmedCert);
    return hash.digest('hex');
}