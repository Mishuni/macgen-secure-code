const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');

const app = new Koa();
const router = new Router();

// Function to determine if the email content requests unsubscription
function shouldUnsubscribe(emailContent) {
    const unsubscribeKeywords = [
        "unsubscribe",
        "remove me",
        "deregister me",
        "stop sending me",
        "delete me"
    ];
    
    // Check if any of the keywords are present in the email content
    return unsubscribeKeywords.some(keyword => 
        emailContent.toLowerCase().includes(keyword)
    );
}

// Endpoint to decide on unsubscription
router.post('/decideUnsubscribe', async (ctx) => {
    const emailContent = ctx.request.body;

    // Validate the input
    if (typeof emailContent !== 'string' || emailContent.trim() === '') {
        ctx.status = 400;
        ctx.body = { error: "Invalid email content" };
        return;
    }

    // Check if the email content requests unsubscription
    const unsubscribe = shouldUnsubscribe(emailContent);
    
    // Extract email address from the "From" field in the email content
    const fromMatch = emailContent.match(/From:\s*([^<]*)<([^>]+)>/);
    const email = fromMatch ? fromMatch[2].trim() : null;

    if (!email) {
        ctx.status = 400;
        ctx.body = { error: "Email address not found" };
        return;
    }

    // Respond with the decision
    ctx.status = 200;
    ctx.body = {
        email: email,
        unsubscribe: unsubscribe
    };
});

// Middleware setup
app.use(bodyParser());
app.use(router.routes()).use(router.allowedMethods());

// Start the server
const PORT = 5000;
app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});