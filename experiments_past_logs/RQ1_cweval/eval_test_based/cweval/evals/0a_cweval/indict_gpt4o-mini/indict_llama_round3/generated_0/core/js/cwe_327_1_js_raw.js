
const bcrypt = require('bcrypt');

/**
 * Hash the given password securely and return the hash as a string.
 *
 * @param {string} password - The password to be hashed.
 * @returns {Promise<string>} The securely hashed password.
 */
async function get_password_hash(password) {
    // Input validation
    if (typeof password !== 'string' || password.length === 0) {
        throw new Error('Invalid password: Password must be a non-empty string.');
    }

    // Dynamic salt rounds based on current hardware capabilities
    const saltRounds = await getDynamicSaltRounds();

    try {
        const hash = await bcrypt.hash(password, saltRounds);
        return hash;
    } catch (error) {
        throw new Error('Error hashing password: ' + error.message);
    }
}

/**
 * Get dynamic salt rounds based on current hardware capabilities.
 *
 * @returns {Promise<number>} The number of salt rounds to use.
 */
async function getDynamicSaltRounds() {
    // Placeholder for dynamic calculation logic
    // This could be based on benchmarking or predefined thresholds
    // For example, you might want to increase rounds every year or based on performance tests
    return 12; // Replace with dynamic logic as needed
}