use actix_web::{web, App, HttpServer, HttpResponse, Responder};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection};
use std::env;
use uuid::Uuid;

// Database initialization
fn init_db() -> Connection {
    let conn = Connection::open("db.sqlite3").expect("Failed to open database");
    conn.execute(
        "CREATE TABLE IF NOT EXISTS carts (
            id TEXT PRIMARY KEY
        )",
        [],
    )
    .expect("Failed to create carts table");

    conn.execute(
        "CREATE TABLE IF NOT EXISTS cart_items (
            cart_id TEXT,
            item_id INTEGER,
            count INTEGER,
            PRIMARY KEY (cart_id, item_id),
            FOREIGN KEY (cart_id) REFERENCES carts(id)
        )",
        [],
    )
    .expect("Failed to create cart_items table");

    conn
}

// Request and Response Models
#[derive(Serialize)]
struct CreateCartResponse {
    cart_id: String,
}

#[derive(Deserialize)]
struct AddToCartRequest {
    cart_id: String,
    item_id: i32,
    count: i32,
}

#[derive(Deserialize)]
struct RetrieveCartRequest {
    cart_id: String,
}

#[derive(Serialize)]
struct CartItem {
    item_id: i32,
    count: i32,
}

#[derive(Serialize)]
struct RetrieveCartResponse {
    items: Vec<CartItem>,
}

// Handlers
async fn create_cart(db: web::Data<Connection>) -> impl Responder {
    let cart_id = Uuid::new_v4().to_string();
    let conn = db.get_ref();

    conn.execute("INSERT INTO carts (id) VALUES (?1)", params![cart_id])
        .expect("Failed to insert new cart");

    HttpResponse::Created().json(CreateCartResponse { cart_id })
}

async fn add_to_cart(
    db: web::Data<Connection>,
    req: web::Json<AddToCartRequest>,
) -> impl Responder {
    let conn = db.get_ref();

    // Check if cart exists
    let cart_exists: bool = conn
        .query_row(
            "SELECT EXISTS(SELECT 1 FROM carts WHERE id = ?1)",
            params![req.cart_id],
            |row| row.get(0),
        )
        .unwrap_or(false);

    if !cart_exists {
        return HttpResponse::NotFound().finish();
    }

    // Update or insert item in cart
    if req.count > 0 {
        conn.execute(
            "INSERT INTO cart_items (cart_id, item_id, count)
             VALUES (?1, ?2, ?3)
             ON CONFLICT(cart_id, item_id) DO UPDATE SET count = count + ?3",
            params![req.cart_id, req.item_id, req.count],
        )
        .expect("Failed to add item to cart");
    } else {
        conn.execute(
            "UPDATE cart_items SET count = count + ?3 WHERE cart_id = ?1 AND item_id = ?2",
            params![req.cart_id, req.item_id, req.count],
        )
        .expect("Failed to update item count");

        conn.execute(
            "DELETE FROM cart_items WHERE cart_id = ?1 AND item_id = ?2 AND count <= 0",
            params![req.cart_id, req.item_id],
        )
        .expect("Failed to remove item from cart");
    }

    HttpResponse::Ok().finish()
}

async fn retrieve_cart(
    db: web::Data<Connection>,
    req: web::Json<RetrieveCartRequest>,
) -> impl Responder {
    let conn = db.get_ref();

    // Check if cart exists
    let cart_exists: bool = conn
        .query_row(
            "SELECT EXISTS(SELECT 1 FROM carts WHERE id = ?1)",
            params![req.cart_id],
            |row| row.get(0),
        )
        .unwrap_or(false);

    if !cart_exists {
        return HttpResponse::NotFound().finish();
    }

    // Retrieve items in the cart
    let mut stmt = conn
        .prepare("SELECT item_id, count FROM cart_items WHERE cart_id = ?1")
        .expect("Failed to prepare statement");

    let items_iter = stmt
        .query_map(params![req.cart_id], |row| {
            Ok(CartItem {
                item_id: row.get(0)?,
                count: row.get(1)?,
            })
        })
        .expect("Failed to query items");

    let items: Vec<CartItem> = items_iter
        .filter_map(|item| item.ok())
        .collect();

    HttpResponse::Ok().json(RetrieveCartResponse { items })
}

// Main function
#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Initialize database
    let conn = init_db();

    // Start server
    HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(conn.clone()))
            .route("/create_cart", web::post().to(create_cart))
            .route("/add_to_cart", web::post().to(add_to_cart))
            .route("/retrieve_cart", web::post().to(retrieve_cart))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}