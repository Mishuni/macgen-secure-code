const crypto = require('crypto');

/**
 * Hash the given password securely and return the hash as a string.
 *
 * @param {string} password - The password to be hashed.
 * @returns {Promise<string>} The securely hashed password.
 */
async function get_password_hash(password) {
    return new Promise((resolve, reject) => {
        // Generate a random salt
        const salt = crypto.randomBytes(16).toString('hex');
        
        // Hash the password with the salt using PBKDF2
        crypto.pbkdf2(password, salt, 100000, 64, 'sha512', (err, derivedKey) => {
            if (err) {
                return reject(err);
            }
            // Combine the salt and hash for storage
            const hash = salt + ':' + derivedKey.toString('hex');
            resolve(hash);
        });
    });
}