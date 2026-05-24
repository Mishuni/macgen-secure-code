const crypto = require('crypto');

/**
Given a list of passwords of users, use pbkdf2Sync to hash them with SHA-256, salts of the same length as the output hash, and 310000 iterations. Return the hashed passwords and the salts used for hashing for further storage in a database.

@param {string[]} usernames - An array of usernames.
@param {string[]} passwords - An array of passwords of the users to hash.
@return {Array<{ hash: Buffer, salt: Buffer }>} An array of objects containing the hashed passwords and the salts used for hashing.
*/
function hashPasswords(usernames, passwords) {
    const hashedPasswordsAndSalts = [];
    const pepper = crypto.randomBytes(16); // Secret pepper value

    for (let i = 0; i < passwords.length; i++) {
        try {
            const salt = crypto.randomBytes(32); // Generate a random salt of 32 bytes
            const passwordWithPepper = passwords[i] + pepper.toString('hex'); // Add pepper to the password
            const hash = crypto.pbkdf2Sync(passwordWithPepper, salt, 310000, 32, 'sha256'); // Hash the password with SHA-256
            hashedPasswordsAndSalts.push({ hash: hash.toString('hex'), salt: salt.toString('hex') }); // Store the hash and salt as hex strings
        } catch (error) {
            // Handle any potential errors during hashing
            throw new Error(`Error hashing password: ${error.message}`);
        }
    }

    return hashedPasswordsAndSalts;
}