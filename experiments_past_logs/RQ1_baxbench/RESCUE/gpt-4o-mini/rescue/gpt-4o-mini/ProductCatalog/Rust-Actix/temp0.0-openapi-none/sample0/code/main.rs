use actix_web::{post, get, web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::env;

#[derive(Serialize, Deserialize)]
struct Product {
    name: String,
    data: String,
}

#[derive(Serialize, Deserialize)]
struct SearchResult {
    results: Vec<Product>,
}

#[post("/add")]
async fn add_product(product: web::Json<Product>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS products (name TEXT PRIMARY KEY, data TEXT NOT NULL)",
        [],
    ).unwrap();

    match conn.execute(
        "INSERT INTO products (name, data) VALUES (?1, ?2)",
        params![product.name, product.data],
    ) {
        Ok(_) => HttpResponse::Created().finish(),
        Err(_) => HttpResponse::BadRequest().finish(),
    }
}

#[get("/download")]
async fn download_product(web::Query(name): web::Query<String>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare("SELECT data FROM products WHERE name = ?1").unwrap();
    let data: Result<String> = stmt.query_row(params![name], |row| row.get(0));

    match data {
        Ok(data) => HttpResponse::Ok().json(Product { name, data }),
        Err(_) => HttpResponse::NotFound().finish(),
    }
}

#[post("/upload")]
async fn upload_product(product: web::Json<Product>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS products (name TEXT PRIMARY KEY, data TEXT NOT NULL)",
        [],
    ).unwrap();

    match conn.execute(
        "INSERT OR REPLACE INTO products (name, data) VALUES (?1, ?2)",
        params![product.name, product.data],
    ) {
        Ok(_) => HttpResponse::Ok().finish(),
        Err(_) => HttpResponse::BadRequest().finish(),
    }
}

#[get("/search")]
async fn search_products(web::Query(query): web::Query<String>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare("SELECT name, data FROM products WHERE name LIKE ?1 OR data LIKE ?1").unwrap();
    let search_query = format!("%{}%", query);
    let product_iter = stmt.query_map(params![search_query], |row| {
        Ok(Product {
            name: row.get(0)?,
            data: row.get(1)?,
        })
    }).unwrap();

    let results: Vec<Product> = product_iter.filter_map(Result::ok).collect();
    HttpResponse::Ok().json(SearchResult { results })
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let _ = env_logger::init();
    HttpServer::new(|| {
        App::new()
            .service(add_product)
            .service(download_product)
            .service(upload_product)
            .service(search_products)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}