
const crypto = require('crypto');

/**
 * Hash the given password securely and return the hash as a string.
 *
 * @param {string} password - The password to be hashed.
 * @returns {Promise<string>} The securely hashed password.
 */
async function get_password_hash(password) {
    return new Promise((resolve, reject) => {
        if (typeof password !== 'string' || password.length === 0) {
            return reject(new Error('Password must be a non-empty string.'));
        }

        const salt = crypto.randomBytes(16).toString('hex'); // Generate a secure random salt
        crypto.pbkdf2(password, salt, 100000, 64, 'sha256', (err, derivedKey) => {
            if (err) {
                return reject(new Error('Error hashing password.'));
            }
            // Return the salt and hash in a format that can be stored
            resolve(`${salt}:${derivedKey.toString('hex')}`);
        });
    });
}