
use actix_web::{web, App, HttpServer, HttpResponse, Responder};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
use uuid::Uuid;
use std::env;

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

async fn create_cart() -> impl Responder {
    let conn = Connection::open("db.sqlite3").expect("Failed to open database");
    let cart_id = Uuid::new_v4().to_string();
    conn.execute("INSERT INTO carts (cart_id) VALUES (?1)", params![cart_id]).unwrap();
    HttpResponse::Created().json(CreateCartResponse { cart_id })
}

async fn add_to_cart(req: web::Json<AddToCartRequest>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").expect("Failed to open database");
    let cart_exists: bool = conn.query_row(
        "SELECT EXISTS(SELECT 1 FROM carts WHERE cart_id = ?1)",
        params![req.cart_id],
        |row| row.get(0),
    ).unwrap();

    if !cart_exists {
        return HttpResponse::NotFound().finish();
    }

    conn.execute(
        "INSERT INTO cart_items (cart_id, item_id, count) VALUES (?1, ?2, ?3)
         ON CONFLICT(cart_id, item_id) DO UPDATE SET count = count + ?3",
        params![req.cart_id, req.item_id, req.count],
    ).unwrap();

    HttpResponse::Ok().finish()
}

async fn retrieve_cart(req: web::Json<RetrieveCartRequest>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").expect("Failed to open database");
    let mut stmt = conn.prepare("SELECT item_id, count FROM cart_items WHERE cart_id = ?1").unwrap();
    let cart_iter = stmt.query_map(params![req.cart_id], |row| {
        Ok(CartItem {
            item_id: row.get(0)?,
            count: row.get(1)?,
        })
    }).unwrap();

    let mut items = Vec::new();
    for item in cart_iter {
        items.push(item.unwrap());
    }

    if items.is_empty() {
        return HttpResponse::NotFound().finish();
    }

    HttpResponse::Ok().json(RetrieveCartResponse { items })
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let conn = Connection::open("db.sqlite3").expect("Failed to open database");
    conn.execute(
        "CREATE TABLE IF NOT EXISTS carts (
            cart_id TEXT PRIMARY KEY
        )",
        [],
    ).unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS cart_items (
            cart_id TEXT,
            item_id INTEGER,
            count INTEGER,
            PRIMARY KEY (cart_id, item_id),
            FOREIGN KEY (cart_id) REFERENCES carts(cart_id)
        )",
        [],
    ).unwrap();

    HttpServer::new(|| {
        App::new()
            .route("/create_cart", web::post().to(create_cart))
            .route("/add_to_cart", web::post().to(add_to_cart))
            .route("/retrieve_cart", web::post().to(retrieve_cart))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}