const bcrypt = require('bcrypt');

async function get_password_hash(password) {
    if (password.length < 8) {
        throw new Error('Password must be at least 8 characters long.');
    }
    const saltRounds = 12;
    const hash = await bcrypt.hash(password, saltRounds);
    return hash;
}