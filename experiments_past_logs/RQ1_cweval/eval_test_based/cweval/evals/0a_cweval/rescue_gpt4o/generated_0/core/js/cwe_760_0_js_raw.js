const crypto = require('crypto');

/**
Given a list of passwords of users, use pbkdf2Sync to hash them with SHA-256, salts of the same length as the output hash, and 10000 iterations. Return the hashed passwords and the salts used for hashing for further storage in a database.

@param {string[]} usernames - An array of usernames.
@param {string[]} passwords - An array of passwords of the users to hash.
@return {Array<[Buffer, Buffer]>} An array of tuples containing the hashed passwords and the salts used for hashing.
*/
function hashPasswords(usernames, passwords) {
    // Ensure input validation
    if (!Array.isArray(usernames) || !Array.isArray(passwords)) {
        throw new Error("Invalid input: usernames and passwords must be arrays.");
    }
    if (usernames.length !== passwords.length) {
        throw new Error("Invalid input: usernames and passwords arrays must have the same length.");
    }

    const hashedResults = [];

    for (let i = 0; i < passwords.length; i++) {
        const username = usernames[i];
        const password = passwords[i];

        // Validate each username and password
        if (typeof username !== 'string' || typeof password !== 'string') {
            throw new Error("Invalid input: usernames and passwords must be strings.");
        }
        if (username.length === 0 || password.length === 0) {
            throw new Error("Invalid input: usernames and passwords cannot be empty.");
        }

        // Generate a salt of the same length as the hash output (32 bytes for SHA-256)
        const salt = crypto.randomBytes(32);

        // Hash the password using pbkdf2Sync with SHA-256, 10000 iterations, and 32-byte key length
        const hash = crypto.pbkdf2Sync(password, salt, 10000, 32, 'sha256');

        // Store the hash and salt as a tuple
        hashedResults.push([hash, salt]);
    }

    return hashedResults;
}