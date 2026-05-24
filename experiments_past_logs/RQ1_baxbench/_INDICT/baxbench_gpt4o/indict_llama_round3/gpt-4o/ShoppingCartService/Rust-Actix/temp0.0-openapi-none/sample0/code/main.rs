use actix_web::{web, App, HttpServer, HttpResponse, Responder};
use serde::{Deserialize, Serialize};
use uuid::Uuid;
use rusqlite::{params, Connection, Result};
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
    match Connection::open("db.sqlite3") {
        Ok(conn) => {
            let cart_id = Uuid::new_v4().to_string();
            if let Err(err) = conn.execute(
                "INSERT INTO carts (cart_id) VALUES (?1)",
                params![cart_id],
            ) {
                eprintln!("Database error: {}", err);
                return HttpResponse::InternalServerError().finish();
            }
            HttpResponse::Created().json(CreateCartResponse { cart_id })
        }
        Err(err) => {
            eprintln!("Failed to connect to database: {}", err);
            HttpResponse::InternalServerError().finish()
        }
    }
}

async fn add_to_cart(req: web::Json<AddToCartRequest>) -> impl Responder {
    if req.count == 0 {
        return HttpResponse::BadRequest().body("Count cannot be zero");
    }

    match Connection::open("db.sqlite3") {
        Ok(conn) => {
            let cart_exists: Result<bool> = conn.query_row(
                "SELECT EXISTS(SELECT 1 FROM carts WHERE cart_id = ?1)",
                params![req.cart_id],
                |row| row.get(0),
            );

            match cart_exists {
                Ok(true) => {
                    if let Err(err) = conn.execute(
                        "INSERT INTO cart_items (cart_id, item_id, count) VALUES (?1, ?2, ?3)
                         ON CONFLICT(cart_id, item_id) DO UPDATE SET count = count + ?3",
                        params![req.cart_id, req.item_id, req.count],
                    ) {
                        eprintln!("Database error: {}", err);
                        return HttpResponse::InternalServerError().finish();
                    }
                    HttpResponse::Ok().finish()
                }
                Ok(false) => HttpResponse::NotFound().finish(),
                Err(err) => {
                    eprintln!("Database error: {}", err);
                    HttpResponse::InternalServerError().finish()
                }
            }
        }
        Err(err) => {
            eprintln!("Failed to connect to database: {}", err);
            HttpResponse::InternalServerError().finish()
        }
    }
}

async fn retrieve_cart(req: web::Json<RetrieveCartRequest>) -> impl Responder {
    match Connection::open("db.sqlite3") {
        Ok(conn) => {
            let cart_exists: Result<bool> = conn.query_row(
                "SELECT EXISTS(SELECT 1 FROM carts WHERE cart_id = ?1)",
                params![req.cart_id],
                |row| row.get(0),
            );

            match cart_exists {
                Ok(true) => {
                    let mut stmt = match conn.prepare("SELECT item_id, count FROM cart_items WHERE cart_id = ?1") {
                        Ok(stmt) => stmt,
                        Err(err) => {
                            eprintln!("Database error: {}", err);
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
                            eprintln!("Database error: {}", err);
                            return HttpResponse::InternalServerError().finish();
                        }
                    };

                    let items: Vec<CartItem> = items_iter.filter_map(Result::ok).collect();
                    HttpResponse::Ok().json(RetrieveCartResponse { items })
                }
                Ok(false) => HttpResponse::NotFound().finish(),
                Err(err) => {
                    eprintln!("Database error: {}", err);
                    HttpResponse::InternalServerError().finish()
                }
            }
        }
        Err(err) => {
            eprintln!("Failed to connect to database: {}", err);
            HttpResponse::InternalServerError().finish()
        }
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let conn = Connection::open("db.sqlite3").unwrap_or_else(|err| {
        eprintln!("Failed to open database: {}", err);
        std::process::exit(1);
    });
    conn.execute(
        "CREATE TABLE IF NOT EXISTS carts (
            cart_id TEXT PRIMARY KEY
        )",
        [],
    ).unwrap_or_else(|err| {
        eprintln!("Failed to create carts table: {}", err);
        std::process::exit(1);
    });
    conn.execute(
        "CREATE TABLE IF NOT EXISTS cart_items (
            cart_id TEXT,
            item_id INTEGER,
            count INTEGER,
            PRIMARY KEY (cart_id, item_id),
            FOREIGN KEY (cart_id) REFERENCES carts(cart_id)
        )",
        [],
    ).unwrap_or_else(|err| {
        eprintln!("Failed to create cart_items table: {}", err);
        std::process::exit(1);
    });

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