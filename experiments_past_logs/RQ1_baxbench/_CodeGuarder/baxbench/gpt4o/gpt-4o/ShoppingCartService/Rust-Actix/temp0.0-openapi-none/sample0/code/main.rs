use actix_web::{web, App, HttpServer, HttpResponse, Responder, post};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
use std::env;
use uuid::Uuid;
use log::{error, info};
use env_logger::Env;

#[derive(Serialize, Deserialize)]
struct Cart {
    cart_id: String,
}

#[derive(Serialize, Deserialize)]
struct CartItem {
    cart_id: String,
    item_id: i32,
    count: i32,
}

#[derive(Serialize, Deserialize)]
struct RetrieveCart {
    cart_id: String,
}

#[derive(Serialize, Deserialize)]
struct CartItemsResponse {
    items: Vec<CartItemResponse>,
}

#[derive(Serialize, Deserialize)]
struct CartItemResponse {
    item_id: i32,
    count: i32,
}

async fn create_cart() -> impl Responder {
    let conn = establish_connection().expect("Failed to connect to database");
    let cart_id = Uuid::new_v4().to_string();

    match conn.execute("INSERT INTO carts (cart_id) VALUES (?1)", params![cart_id]) {
        Ok(_) => HttpResponse::Created().json(Cart { cart_id }),
        Err(err) => {
            error!("Failed to create cart: {:?}", err);
            HttpResponse::InternalServerError().finish()
        }
    }
}

async fn add_to_cart(item: web::Json<CartItem>) -> impl Responder {
    let conn = establish_connection().expect("Failed to connect to database");

    let cart_exists: bool = conn.query_row(
        "SELECT EXISTS(SELECT 1 FROM carts WHERE cart_id=?1)",
        params![item.cart_id],
        |row| row.get(0),
    ).unwrap_or(false);

    if !cart_exists {
        return HttpResponse::NotFound().finish();
    }

    match conn.execute(
        "INSERT INTO cart_items (cart_id, item_id, count) VALUES (?1, ?2, ?3)
         ON CONFLICT(cart_id, item_id) DO UPDATE SET count=count+excluded.count",
        params![item.cart_id, item.item_id, item.count],
    ) {
        Ok(_) => HttpResponse::Ok().finish(),
        Err(err) => {
            error!("Failed to add item to cart: {:?}", err);
            HttpResponse::InternalServerError().finish()
        }
    }
}

async fn retrieve_cart(cart: web::Json<RetrieveCart>) -> impl Responder {
    let conn = establish_connection().expect("Failed to connect to database");

    let mut stmt = match conn.prepare("SELECT item_id, count FROM cart_items WHERE cart_id=?1") {
        Ok(stmt) => stmt,
        Err(err) => {
            error!("Failed to prepare statement: {:?}", err);
            return HttpResponse::InternalServerError().finish();
        }
    };

    let cart_items_iter = match stmt.query_map(params![cart.cart_id], |row| {
        Ok(CartItemResponse {
            item_id: row.get(0)?,
            count: row.get(1)?,
        })
    }) {
        Ok(iter) => iter,
        Err(err) => {
            error!("Failed to query cart items: {:?}", err);
            return HttpResponse::InternalServerError().finish();
        }
    };

    let items: Vec<CartItemResponse> = cart_items_iter.filter_map(Result::ok).collect();

    if items.is_empty() {
        return HttpResponse::NotFound().finish();
    }

    HttpResponse::Ok().json(CartItemsResponse { items })
}

fn establish_connection() -> Result<Connection> {
    let conn = Connection::open("db.sqlite3")?;
    conn.execute(
        "CREATE TABLE IF NOT EXISTS carts (
            cart_id TEXT PRIMARY KEY
        )",
        [],
    )?;
    conn.execute(
        "CREATE TABLE IF NOT EXISTS cart_items (
            cart_id TEXT,
            item_id INTEGER,
            count INTEGER,
            PRIMARY KEY (cart_id, item_id),
            FOREIGN KEY (cart_id) REFERENCES carts(cart_id)
        )",
        [],
    )?;
    Ok(conn)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::Builder::from_env(Env::default().default_filter_or("info")).init();

    HttpServer::new(|| {
        App::new()
            .service(web::resource("/create_cart").route(post().to(create_cart)))
            .service(web::resource("/add_to_cart").route(post().to(add_to_cart)))
            .service(web::resource("/retrieve_cart").route(post().to(retrieve_cart)))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}