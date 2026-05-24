const bcrypt = require('bcrypt');

async function get_password_hash(password) {
    const saltRounds = 10;
    const hash = await bcrypt.hash(password, saltRounds);
    return hash;
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
