const Koa = require('koa');
const Router = require('koa-router');
const koaBody = require('@koa/multer')();
const sqlite3 = require('sqlite3').verbose();
const sanitizeHtml = require('sanitize-html');

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

// Middleware to handle multipart/form-data
router.post('/add_profile', koaBody.fields([{ name: 'username' }, { name: 'profile_page' }, { name: 'profile_photo' }]), async (ctx) => {
    const { username } = ctx.request.body;
    const { profile_page } = ctx.request.body;
    const profile_photo = ctx.request.files.profile_photo[0].buffer;

    // Validate input
    if (!username || !profile_page || !profile_photo) {
        ctx.status = 400;
        ctx.body = 'Invalid input';
        return;
    }

    // Sanitize HTML content
    const sanitizedProfilePage = sanitizeHtml(profile_page, {
        allowedTags: sanitizeHtml.defaults.allowedTags.concat(['img']),
        allowedAttributes: {
            ...sanitizeHtml.defaults.allowedAttributes,
            'img': ['src', 'alt']
        }
    });

    // Validate file type and size
    if (!ctx.request.files.profile_photo[0].mimetype === 'image/png' || ctx.request.files.profile_photo[0].size > 2 * 1024 * 1024) {
        ctx.status = 400;
        ctx.body = 'Invalid file type or size';
        return;
    }

    db.serialize(() => {
        db.run(`INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)`, [username, sanitizedProfilePage, profile_photo], function(err) {
            if (err) {
                if (err.message.includes('UNIQUE constraint failed')) {
                    ctx.status = 403;
                    ctx.body = 'Profile already exists, creation forbidden';
                } else {
                    ctx.status = 400;
                    ctx.body = 'Invalid input';
                }
            } else {
                ctx.status = 201;
                ctx.body = 'Profile created successfully';
            }
        });
    });
});

router.get('/profile/:username', async (ctx) => {
    const { username } = ctx.params;

    db.get(`SELECT profile_page FROM profiles WHERE username = ?`, [username], (err, row) => {
        if (err || !row) {
            ctx.status = 404;
            ctx.body = 'Profile not found';
        } else {
            ctx.status = 200;
            ctx.type = 'html';
            ctx.body = row.profile_page;
        }
    });
});

router.get('/profile-photo/:username', async (ctx) => {
    const { username } = ctx.params;

    db.get(`SELECT profile_photo FROM profiles WHERE username = ?`, [username], (err, row) => {
        if (err || !row) {
            ctx.status = 404;
            ctx.body = 'Profile photo not found';
        } else {
            ctx.status = 200;
            ctx.type = 'image/png';
            ctx.body = row.profile_photo;
        }
    });
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});