use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::env;

#[derive(Serialize, Deserialize)]
struct CreateCartResponse {
    cart_id: String,
}

#[derive(Serialize, Deserialize)]
struct AddToCartRequest {
    cart_id: String,
    item_id: i32,
    count: i32,
}

#[derive(Serialize, Deserialize)]
struct RetrieveCartRequest {
    cart_id: String,
}

#[derive(Serialize, Deserialize)]
struct CartItem {
    item_id: i32,
    count: i32,
}

#[derive(Serialize, Deserialize)]
struct RetrieveCartResponse {
    items: Vec<CartItem>,
}

fn establish_connection() -> Result<Connection> {
    Connection::open("db.sqlite3")
}

fn initialize_database() -> Result<()> {
    let conn = establish_connection()?;
    conn.execute(
        "CREATE TABLE IF NOT EXISTS carts (
            id TEXT PRIMARY KEY
        )",
        [],
    )?;
    conn.execute(
        "CREATE TABLE IF NOT EXISTS cart_items (
            cart_id TEXT,
            item_id INTEGER,
            count INTEGER,
            PRIMARY KEY (cart_id, item_id)
        )",
        [],
    )?;
    Ok(())
}

#[post("/create_cart")]
async fn create_cart() -> impl Responder {
    let conn = establish_connection().unwrap();
    let cart_id = uuid::Uuid::new_v4().to_string();
    conn.execute("INSERT INTO carts (id) VALUES (?1)", params![cart_id]).unwrap();
    HttpResponse::Created().json(CreateCartResponse { cart_id })
}

#[post("/add_to_cart")]
async fn add_to_cart(item: web::Json<AddToCartRequest>) -> impl Responder {
    if item.count == 0 {
        return HttpResponse::BadRequest().body("Count must be non-zero");
    }

    let conn = establish_connection().unwrap();
    let result = conn.execute(
        "INSERT INTO cart_items (cart_id, item_id, count) VALUES (?1, ?2, ?3)
         ON CONFLICT(cart_id, item_id) DO UPDATE SET count = count + ?3",
        params![item.cart_id, item.item_id, item.count],
    );

    match result {
        Ok(_) => HttpResponse::Ok().finish(),
        Err(err) => {
            eprintln!("Database error: {}", err);
            HttpResponse::InternalServerError().finish()
        }
    }
}

#[post("/retrieve_cart")]
async fn retrieve_cart(request: web::Json<RetrieveCartRequest>) -> impl Responder {
    let conn = establish_connection().unwrap();
    let mut stmt = conn.prepare("SELECT item_id, count FROM cart_items WHERE cart_id = ?1").unwrap();
    let items_iter = stmt.query_map(params![request.cart_id], |row| {
        Ok(CartItem {
            item_id: row.get(0)?,
            count: row.get(1)?,
        })
    }).unwrap();

    let items: Vec<CartItem> = items_iter.filter_map(Result::ok).collect();

    if items.is_empty() {
        HttpResponse::NotFound().finish()
    } else {
        HttpResponse::Ok().json(RetrieveCartResponse { items })
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let _ = env_logger::init();
    initialize_database().unwrap();
    HttpServer::new(|| {
        App::new()
            .service(create_cart)
            .service(add_to_cart)
            .service(retrieve_cart)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}