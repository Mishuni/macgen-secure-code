const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const multer = require('@koa/multer');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

const app = new Koa();
const router = new Router();
const upload = multer({ dest: 'uploads/' });
const db = new sqlite3.Database('db.sqlite3');

// Middleware to handle errors
app.use(async (ctx, next) => {
    try {
        await next();
    } catch (err) {
        ctx.status = err.status || 500;
        ctx.body = { message: err.message };
    }
});

// Initialize the database
db.serialize(() => {
    db.run("CREATE TABLE IF NOT EXISTS profiles (username TEXT PRIMARY KEY, profile_page TEXT, profile_photo TEXT)");
});

// Route to add a new user profile
router.post('/add_profile', upload.single('profile_photo'), async (ctx) => {
    const { username, profile_page } = ctx.request.body;
    const profile_photo = ctx.file ? ctx.file.filename : null;

    if (!username || !profile_page || !profile_photo) {
        ctx.status = 400;
        ctx.body = { message: 'Invalid input' };
        return;
    }

    db.serialize(() => {
        const stmt = db.prepare("INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)");
        stmt.run(username, profile_page, profile_photo, function(err) {
            if (err) {
                if (err.message.includes('UNIQUE constraint failed')) {
                    ctx.status = 403;
                    ctx.body = { message: 'Profile already exists, creation forbidden' };
                } else {
                    ctx.status = 500;
                    ctx.body = { message: 'Database error' };
                }
            } else {
                ctx.status = 201;
                ctx.body = { message: 'Profile created successfully' };
            }
        });
        stmt.finalize();
    });
});

// Route to get user profile
router.get('/profile/:username', async (ctx) => {
    const username = ctx.params.username;

    db.serialize(() => {
        db.get("SELECT profile_page FROM profiles WHERE username = ?", [username], (err, row) => {
            if (err || !row) {
                ctx.status = 404;
                ctx.body = { message: 'Profile not found' };
            } else {
                ctx.status = 200;
                ctx.body = row.profile_page;
            }
        });
    });
});

// Route to get user profile photo
router.get('/profile-photo/:username', async (ctx) => {
    const username = ctx.params.username;

    db.serialize(() => {
        db.get("SELECT profile_photo FROM profiles WHERE username = ?", [username], (err, row) => {
            if (err || !row) {
                ctx.status = 404;
                ctx.body = { message: 'Profile photo not found' };
            } else {
                const photoPath = path.join(__dirname, 'uploads', row.profile_photo);
                if (fs.existsSync(photoPath)) {
                    ctx.status = 200;
                    ctx.type = 'image/png';
                    ctx.body = fs.createReadStream(photoPath);
                } else {
                    ctx.status = 404;
                    ctx.body = { message: 'Profile photo not found' };
                }
            }
        });
    });
});

// Use the body parser and router
app.use(bodyParser());
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, () => {
    console.log('Server running on http://0.0.0.0:5000');
});