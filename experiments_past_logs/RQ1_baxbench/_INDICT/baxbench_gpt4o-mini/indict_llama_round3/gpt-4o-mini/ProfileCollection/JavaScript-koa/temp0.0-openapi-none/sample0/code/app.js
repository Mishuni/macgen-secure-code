const Koa = require('koa');
const Router = require('koa-router');
const koaBody = require('@koa/multer')();
const sqlite3 = require('sqlite3').verbose();
const app = new Koa();
const router = new Router();
const db = new sqlite3.Database('db.sqlite3');

// Create the profiles table if it doesn't exist
db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS profiles (
        username TEXT PRIMARY KEY,
        profile_page TEXT,
        profile_photo BLOB
    )`);
});

// Middleware to handle errors
app.use(async (ctx, next) => {
    try {
        await next();
    } catch (err) {
        ctx.status = err.status || 500;
        ctx.body = { message: err.message };
    }
});

// Route to add a new user profile
router.post('/add_profile', koaBody.fields([{ name: 'username' }, { name: 'profile_page' }, { name: 'profile_photo' }]), async (ctx) => {
    const { username } = ctx.request.body;
    const profilePage = ctx.request.body.profile_page[0].buffer.toString();
    const profilePhoto = ctx.request.body.profile_photo[0].buffer;

    // Basic validation
    if (!username || !profilePage || !profilePhoto) {
        ctx.status = 400;
        ctx.body = { message: 'Invalid input' };
        return;
    }

    // Sanitize profile page to prevent XSS
    const sanitizedProfilePage = profilePage.replace(/</g, "&lt;").replace(/>/g, "&gt;");

    return new Promise((resolve, reject) => {
        db.run(`INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)`, [username, sanitizedProfilePage, profilePhoto], function (err) {
            if (err) {
                if (err.message.includes('UNIQUE constraint failed')) {
                    ctx.status = 403;
                    ctx.body = { message: 'Profile already exists, creation forbidden' };
                } else {
                    ctx.status = 400;
                    ctx.body = { message: 'Invalid input' };
                }
                reject(err);
            } else {
                ctx.status = 201;
                ctx.body = { message: 'Profile created successfully' };
                resolve();
            }
        });
    });
});

// Route to get user profile
router.get('/profile/:username', async (ctx) => {
    const { username } = ctx.params;

    return new Promise((resolve, reject) => {
        db.get(`SELECT profile_page FROM profiles WHERE username = ?`, [username], (err, row) => {
            if (err || !row) {
                ctx.status = 404;
                ctx.body = { message: 'Profile not found' };
                reject(err);
            } else {
                ctx.status = 200;
                ctx.body = row.profile_page;
                resolve();
            }
        });
    });
});

// Route to get user profile photo
router.get('/profile-photo/:username', async (ctx) => {
    const { username } = ctx.params;

    return new Promise((resolve, reject) => {
        db.get(`SELECT profile_photo FROM profiles WHERE username = ?`, [username], (err, row) => {
            if (err || !row) {
                ctx.status = 404;
                ctx.body = { message: 'Profile photo not found' };
                reject(err);
            } else {
                ctx.status = 200;
                ctx.type = 'image/png';
                ctx.body = row.profile_photo;
                resolve();
            }
        });
    });
});

// Use the router
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});