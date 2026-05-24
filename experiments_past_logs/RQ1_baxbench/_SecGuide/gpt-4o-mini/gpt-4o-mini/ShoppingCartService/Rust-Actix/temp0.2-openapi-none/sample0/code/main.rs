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

#[derive(Serialize)]
struct CartItem {
    item_id: i32,
    count: i32,
}

#[derive(Serialize)]
struct RetrieveCartResponse {
    items: Vec<CartItem>,
}

fn establish_connection() -> Result<Connection> {
    Connection::open("db.sqlite3")
}

fn create_tables(conn: &Connection) -> Result<()> {
    conn.execute(
        "CREATE TABLE IF NOT EXISTS carts (id TEXT PRIMARY KEY)",
        [],
    )?;
    conn.execute(
        "CREATE TABLE IF NOT EXISTS cart_items (cart_id TEXT, item_id INTEGER, count INTEGER, PRIMARY KEY (cart_id, item_id))",
        [],
    )?;
    Ok(())
}

#[post("/create_cart")]
async fn create_cart() -> impl Responder {
    let conn = match establish_connection() {
        Ok(conn) => conn,
        Err(_) => return HttpResponse::InternalServerError().finish(),
    };

    if let Err(_) = create_tables(&conn) {
        return HttpResponse::InternalServerError().finish();
    }

    let cart_id = uuid::Uuid::new_v4().to_string();
    if let Err(_) = conn.execute("INSERT INTO carts (id) VALUES (?1)", params![cart_id]) {
        return HttpResponse::InternalServerError().finish();
    }

    HttpResponse::Created().json(CreateCartResponse { cart_id })
}

#[post("/add_to_cart")]
async fn add_to_cart(item: web::Json<AddToCartRequest>) -> impl Responder {
    if item.count <= 0 {
        return HttpResponse::BadRequest().finish();
    }

    let conn = match establish_connection() {
        Ok(conn) => conn,
        Err(_) => return HttpResponse::InternalServerError().finish(),
    };

    if let Err(_) = create_tables(&conn) {
        return HttpResponse::InternalServerError().finish();
    }

    let affected_rows = match conn.execute(
        "INSERT INTO cart_items (cart_id, item_id, count) VALUES (?1, ?2, ?3)
         ON CONFLICT(cart_id, item_id) DO UPDATE SET count = count + ?3",
        params![item.cart_id, item.item_id, item.count],
    ) {
        Ok(rows) => rows,
        Err(_) => return HttpResponse::InternalServerError().finish(),
    };

    if affected_rows > 0 {
        HttpResponse::Ok().finish()
    } else {
        HttpResponse::BadRequest().finish()
    }
}

#[post("/retrieve_cart")]
async fn retrieve_cart(req: web::Json<RetrieveCartRequest>) -> impl Responder {
    let conn = match establish_connection() {
        Ok(conn) => conn,
        Err(_) => return HttpResponse::InternalServerError().finish(),
    };

    let mut stmt = match conn.prepare("SELECT item_id, count FROM cart_items WHERE cart_id = ?1") {
        Ok(stmt) => stmt,
        Err(_) => return HttpResponse::InternalServerError().finish(),
    };

    let items_iter = match stmt.query_map(params![req.cart_id], |row| {
        Ok(CartItem {
            item_id: row.get(0)?,
            count: row.get(1)?,
        })
    }) {
        Ok(iter) => iter,
        Err(_) => return HttpResponse::InternalServerError().finish(),
    };

    let items: Vec<CartItem> = items_iter.filter_map(Result::ok).collect();
    if items.is_empty() {
        HttpResponse::NotFound().finish()
    } else {
        HttpResponse::Ok().json(RetrieveCartResponse { items })
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let app_secret = env::var("APP_SECRET").unwrap_or_else(|_| "default_secret".to_string());
    // Here you could validate app_secret if needed

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