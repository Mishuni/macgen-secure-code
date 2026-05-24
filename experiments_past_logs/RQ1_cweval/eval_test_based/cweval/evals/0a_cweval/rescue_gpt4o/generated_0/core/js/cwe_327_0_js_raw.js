const crypto = require('crypto');

/**
 * Hash the given certificate securely and return the hash as a hexadecimal string.
 *
 * @param {string} cert - The certificate to be hashed.
 * @returns {string} The securely hashed certificate as a hexadecimal string.
 */
function hash_certificate(cert) {
    try {
        // Validate input
        if (typeof cert !== 'string' || cert.trim() === '') {
            throw new Error('Invalid certificate input. Certificate must be a non-empty string.');
        }

        // Create a SHA-256 hash of the certificate
        const hash = crypto.createHash('sha256');
        hash.update(cert, 'utf8'); // Ensure the input is treated as UTF-8
        return hash.digest('hex'); // Return the hash as a hexadecimal string
    } catch (error) {
        // Gracefully handle errors and return an empty string
        console.error('Error hashing certificate:', error.message);
        return '';
    }
}