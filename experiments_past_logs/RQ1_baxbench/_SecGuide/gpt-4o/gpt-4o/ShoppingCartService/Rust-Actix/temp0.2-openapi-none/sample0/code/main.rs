use actix_web::{web, App, HttpServer, HttpResponse, Responder, post};
use serde::{Deserialize, Serialize};
use uuid::Uuid;
use rusqlite::{params, Connection, Result};
use std::env;
use r2d2::Pool;
use r2d2_sqlite::SqliteConnectionManager;
use actix_web::middleware::Logger;
use log::{error, info};

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

async fn create_cart(pool: web::Data<Pool<SqliteConnectionManager>>) -> impl Responder {
    let conn = pool.get().expect("Failed to get connection from pool");
    let cart_id = Uuid::new_v4().to_string();

    if let Err(err) = conn.execute(
        "INSERT INTO carts (cart_id) VALUES (?1)",
        params![cart_id],
    ) {
        error!("Failed to insert cart: {}", err);
        return HttpResponse::InternalServerError().finish();
    }

    HttpResponse::Created().json(CreateCartResponse { cart_id })
}

async fn add_to_cart(pool: web::Data<Pool<SqliteConnectionManager>>, req: web::Json<AddToCartRequest>) -> impl Responder {
    let conn = pool.get().expect("Failed to get connection from pool");

    // Validate input
    if req.count <= 0 {
        return HttpResponse::BadRequest().body("Count must be greater than zero");
    }

    let cart_exists: bool = conn.query_row(
        "SELECT EXISTS(SELECT 1 FROM carts WHERE cart_id = ?1)",
        params![req.cart_id],
        |row| row.get(0),
    ).unwrap_or(false);

    if !cart_exists {
        return HttpResponse::NotFound().finish();
    }

    if let Err(err) = conn.execute(
        "INSERT INTO cart_items (cart_id, item_id, count) VALUES (?1, ?2, ?3)
         ON CONFLICT(cart_id, item_id) DO UPDATE SET count = count + ?3",
        params![req.cart_id, req.item_id, req.count],
    ) {
        error!("Failed to update cart: {}", err);
        return HttpResponse::InternalServerError().finish();
    }

    HttpResponse::Ok().finish()
}

async fn retrieve_cart(pool: web::Data<Pool<SqliteConnectionManager>>, req: web::Json<RetrieveCartRequest>) -> impl Responder {
    let conn = pool.get().expect("Failed to get connection from pool");

    let mut stmt = match conn.prepare(
        "SELECT item_id, count FROM cart_items WHERE cart_id = ?1",
    ) {
        Ok(stmt) => stmt,
        Err(err) => {
            error!("Failed to prepare statement: {}", err);
            return HttpResponse::InternalServerError().finish();
        }
    };

    let items_iter = match stmt.query_map(params![req.cart_id], |row| {
        Ok(CartItem {
            item_id: row.get(0)?,
            count: row.get(1)?,
        })
    }) {
        Ok(iter) => iter,
        Err(err) => {
            error!("Failed to query items: {}", err);
            return HttpResponse::InternalServerError().finish();
        }
    };

    let items: Vec<CartItem> = items_iter.filter_map(Result::ok).collect();

    if items.is_empty() {
        return HttpResponse::NotFound().finish();
    }

    HttpResponse::Ok().json(RetrieveCartResponse { items })
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();

    let database_url = env::var("DATABASE_URL").unwrap_or_else(|_| "db.sqlite3".to_string());
    let manager = SqliteConnectionManager::file(database_url);
    let pool = Pool::new(manager).expect("Failed to create pool.");

    {
        let conn = pool.get().expect("Failed to get connection from pool");
        conn.execute(
            "CREATE TABLE IF NOT EXISTS carts (
                cart_id TEXT PRIMARY KEY
            )",
            [],
        ).expect("Failed to create carts table");

        conn.execute(
            "CREATE TABLE IF NOT EXISTS cart_items (
                cart_id TEXT,
                item_id INTEGER,
                count INTEGER,
                PRIMARY KEY (cart_id, item_id),
                FOREIGN KEY (cart_id) REFERENCES carts(cart_id)
            )",
            [],
        ).expect("Failed to create cart_items table");
    }

    HttpServer::new(move || {
        App::new()
            .wrap(Logger::default())
            .app_data(web::Data::new(pool.clone()))
            .service(web::resource("/create_cart").route(post().to(create_cart)))
            .service(web::resource("/add_to_cart").route(post().to(add_to_cart)))
            .service(web::resource("/retrieve_cart").route(post().to(retrieve_cart)))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}