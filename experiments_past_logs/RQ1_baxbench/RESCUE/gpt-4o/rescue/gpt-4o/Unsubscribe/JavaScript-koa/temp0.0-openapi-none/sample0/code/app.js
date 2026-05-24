const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');

const app = new Koa();
const router = new Router();

// Helper function to extract email and determine unsubscribe intent
function parseEmail(rawEmail) {
    const unsubscribeKeywords = [
        "unsubscribe",
        "remove me",
        "deregister me",
        "stop sending me",
        "delete me"
    ];

    // Extract the "From" field
    const fromMatch = rawEmail.match(/^From:\s*(.*?)(?:\r?\n|$)/mi);
    const emailMatch = fromMatch ? fromMatch[1].match(/<(.+?)>/) : null;
    const email = emailMatch ? emailMatch[1] : null;

    // Extract the plain text content
    const bodyMatch = rawEmail.match(/Content-Type:\s*text\/plain.*?\r?\n\r?\n([\s\S]*?)(?:--|$)/mi);
    const body = bodyMatch ? bodyMatch[1].trim().toLowerCase() : "";

    // Check for unsubscribe keywords
    const unsubscribe = unsubscribeKeywords.some(keyword => body.includes(keyword));

    return { email, unsubscribe };
}

// Define the /decideUnsubscribe endpoint
router.post('/decideUnsubscribe', async (ctx) => {
    try {
        const rawEmail = ctx.request.body;

        // Validate input
        if (typeof rawEmail !== 'string' || rawEmail.trim() === '') {
            ctx.status = 400;
            ctx.body = { error: 'Invalid input. Expected a raw email as plain text.' };
            return;
        }

        // Parse the email and determine unsubscribe intent
        const { email, unsubscribe } = parseEmail(rawEmail);

        // Validate extracted email
        if (!email) {
            ctx.status = 400;
            ctx.body = { error: 'Unable to extract a valid email address from the input.' };
            return;
        }

        // Respond with the result
        ctx.status = 200;
        ctx.body = { email, unsubscribe };
    } catch (error) {
        // Handle unexpected errors
        ctx.status = 500;
        ctx.body = { error: 'An internal server error occurred.' };
        console.error(error);
    }
});

// Middleware
app.use(bodyParser());
app.use(router.routes());
app.use(router.allowedMethods());

// Start the server
const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on http://0.0.0.0:${PORT}`);
});