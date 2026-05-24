
const bcrypt = require('bcrypt');

/**
 * Hash the given password securely and return the hash as a string.
 *
 * @param {string} password - The password to be hashed.
 * @returns {Promise<string>} The securely hashed password.
 */
async function get_password_hash(password) {
    const saltRounds = 12; // A reasonable default for bcrypt
    return await bcrypt.hash(password, saltRounds);
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
