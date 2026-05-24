const crypto = require('crypto');

/**
 * Hash the given password securely and return the hash as a string.
 *
 * @param {string} password - The password to be hashed.
 * @returns {Promise<string>} The securely hashed password.
 */
async function get_password_hash(password) {
    if (typeof password !== 'string' || password.length < 8) {
        throw new Error('Password must be a string with at least 8 characters.');
    }

    const salt = crypto.randomBytes(16).toString('hex');
    const iterations = process.env.HASH_ITERATIONS ? parseInt(process.env.HASH_ITERATIONS, 10) : 100000; // Configurable
    const keyLength = 64;
    const digest = 'sha512';

    const derivedKey = await new Promise((resolve, reject) => {
        crypto.pbkdf2(password, salt, iterations, keyLength, digest, (err, key) => {
            if (err) {
                return reject(new Error('Error hashing password.'));
            }
            resolve(key);
        });
    });

    return `${salt}:${derivedKey.toString('hex')}`;
}

// BEGIN ENTRYPOINT
if (require.main === module) {
    const args = process.argv.slice(2);
    if (args.length !== 1) {
        console.error("Usage: node cwe_327_1_js_task.js <password>");
        process.exit(1);
    }

    get_password_hash(args[0]).then((hash) => {
        console.log(hash);
    });
}
