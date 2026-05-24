const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');

const app = new Koa();
const router = new Router();

const unsubscribeKeywords = [
    "unsubscribe",
    "remove me",
    "deregister me",
    "stop sending me",
    "delete me"
];

const shouldUnsubscribe = (emailContent) => {
    const lowerCaseContent = emailContent.toLowerCase();
    return unsubscribeKeywords.some(keyword => lowerCaseContent.includes(keyword));
};

const isValidEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
};

router.post('/decideUnsubscribe', async (ctx) => {
    const emailContent = ctx.request.body;

    if (typeof emailContent !== 'string') {
        ctx.status = 400;
        ctx.body = { error: 'Invalid input, expected plain text email content.' };
        return;
    }

    const emailAddressMatch = emailContent.match(/From:\s*([^<>\s]+@[^<>\s]+)/);
    const emailAddress = emailAddressMatch ? emailAddressMatch[1].trim() : null;

    if (!emailAddress || !isValidEmail(emailAddress)) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid email address.' };
        return;
    }

    ctx.body = {
        email: emailAddress,
        unsubscribe: shouldUnsubscribe(emailContent)
    };
});

app.use(bodyParser());
app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
});