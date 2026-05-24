
import { createHash } from 'crypto';

/**
 * Hash the given certificate securely and return the hash as a hexadecimal string.
 *
 * @param {string} cert - The certificate to be hashed.
 * @returns {string} The securely hashed certificate as a hexadecimal string.
 */
function hash_certificate(cert) {
    // Create a SHA-256 hash instance
    const hash = createHash('sha256');
    
    // Update the hash with the certificate data
    hash.update(cert);
    
    // Return the hash as a hexadecimal string
    return hash.digest('hex');
}