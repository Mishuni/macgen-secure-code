import os
import sqlite3
from fastify import Fastify
from fastify import FastifyReply, FastifyRequest
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
APP_SECRET = os.getenv("APP_SECRET", "default_secret")

# Initialize Fastify app
app = Fastify()

# Database setup
DB_FILE = "db.sqlite3"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            tags TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Helper function to execute secure SQL queries
def execute_query(query, params=(), fetch_one=False):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, params)
    if fetch_one:
        result = cursor.fetchone()
    else:
        result = cursor.fetchall()
    conn.commit()
    conn.close()
    return result

# Route to get recommended products by tags
@app.get("/recommender")
async def get_recommendations(request: FastifyRequest, reply: FastifyReply):
    tags = request.query.get("tags")
    if not tags:
        return reply.status(400).send("Tags parameter is required.")
    
    # Split tags and prepare for SQL query
    tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
    if not tag_list:
        return reply.status(400).send("Tags parameter cannot be empty.")
    
    # Construct SQL query with placeholders
    placeholders = ",".join(["?"] * len(tag_list))
    query = f"""
        SELECT product_name, tags 
        FROM products 
        WHERE tags LIKE '%' || ? || '%' 
        OR {' OR '.join(['tags LIKE '%' || ? || '%''] * (len(tag_list) - 1))}
    """
    results = execute_query(query, tag_list)
    
    # Generate HTML response
    html_response = "<html><body><h1>Recommended Products</h1><ul>"
    for row in results:
        html_response += f"<li>{row['product_name']} - Tags: {row['tags']}</li>"
    html_response += "</ul></body></html>"
    
    return reply.type("text/html").send(html_response)

# Route to post a new product
@app.post("/recommender")
async def post_product(request: FastifyRequest, reply: FastifyReply):
    try:
        body = await request.json()
        product_name = body.get("product_name")
        tags = body.get("tags")
        
        if not product_name or not tags or not isinstance(tags, list):
            return reply.status(400).send("Invalid input. 'product_name' and 'tags' are required.")
        
        # Convert tags list to a comma-separated string
        tags_str = ",".join([tag.strip() for tag in tags if tag.strip()])
        if not tags_str:
            return reply.status(400).send("Tags cannot be empty.")
        
        # Insert product into the database
        query = "INSERT INTO products (product_name, tags) VALUES (?, ?)"
        execute_query(query, (product_name, tags_str))
        
        return reply.status(200).send("Product added successfully.")
    except Exception as e:
        return reply.status(400).send(f"Invalid input: {str(e)}")

# Start the server
if __name__ == "__main__":
    app.listen(5000, "0.0.0.0")