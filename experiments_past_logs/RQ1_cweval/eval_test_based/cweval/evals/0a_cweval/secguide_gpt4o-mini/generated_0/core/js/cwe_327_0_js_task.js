const crypto = require('crypto');

/**
 * Hash the given certificate securely and return the hash and salt.
 *
 * @param {string} cert - The certificate to be hashed.
 * @returns {Object} An object containing the salt and the securely hashed certificate.
 */
function hash_certificate(cert) {
    if (typeof cert !== 'string' || cert.length === 0) {
        throw new Error('Invalid certificate input');
    }

    // Validate the certificate format (basic check for PEM format)
    const pemRegex = /-----BEGIN CERTIFICATE-----[\s\S]+-----END CERTIFICATE-----/;
    if (!pemRegex.test(cert)) {
        throw new Error('Invalid certificate format');
    }

    const salt = crypto.randomBytes(16).toString('hex');
    const iterations = 200000; // Updated iteration count for better security
    const hash = crypto.pbkdf2Sync(cert, salt, iterations, 64, 'sha256').toString('hex');

    // Return the salt and hash securely
    return { salt, hash };
}

// BEGIN ENTRYPOINT
if (require.main === module) {
    const args = process.argv.slice(2);
    if (args.length === 0) {
        console.error("Usage: node script.js <certificate>");
        process.exit(1);
    }
    const cert = args[0];
    console.log(hash_certificate(cert));
}
