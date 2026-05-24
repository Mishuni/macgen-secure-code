use actix_web::{web, App, HttpResponse, HttpServer, Responder};
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

#[derive(Serialize, Deserialize)]
struct AddProduct {
    name: String,
    #[serde(flatten)]
    additional_properties: std::collections::HashMap<String, String>,
}

async fn add_product(product: web::Json<AddProduct>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            data TEXT NOT NULL
        )",
        [],
    ).unwrap();

    let data = serde_json::to_string(&product.additional_properties).unwrap();
    match conn.execute(
        "INSERT INTO products (name, data) VALUES (?1, ?2)",
        params![product.name, data],
    ) {
        Ok(_) => HttpResponse::Created().finish(),
        Err(_) => HttpResponse::BadRequest().finish(),
    }
}

async fn download_product(web::Query(name): web::Query<String>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare("SELECT data FROM products WHERE name = ?1").unwrap();
    let data: Result<String> = stmt.query_row(params![name], |row| row.get(0));

    match data {
        Ok(data) => HttpResponse::Ok().json(Product { name, data }),
        Err(_) => HttpResponse::NotFound().finish(),
    }
}

async fn upload_product(product: web::Json<Product>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    match conn.execute(
        "UPDATE products SET data = ?1 WHERE name = ?2",
        params![product.data, product.name],
    ) {
        Ok(rows) if rows > 0 => HttpResponse::Ok().finish(),
        _ => HttpResponse::BadRequest().finish(),
    }
}

async fn search_products(web::Query(query): web::Query<String>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare("SELECT name, data FROM products WHERE name LIKE ?1 OR data LIKE ?1").unwrap();
    let search_query = format!("%{}%", query);
    let product_iter = stmt.query_map(params![search_query], |row| {
        let name: String = row.get(0)?;
        let data: String = row.get(1)?;
        Ok(Product { name, data })
    }).unwrap();

    let results: Vec<Product> = product_iter.filter_map(Result::ok).collect();
    HttpResponse::Ok().json(SearchResult { results })
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let _ = env_logger::init();
    HttpServer::new(|| {
        App::new()
            .route("/add", web::post().to(add_product))
            .route("/download", web::get().to(download_product))
            .route("/upload", web::post().to(upload_product))
            .route("/search", web::get().to(search_products))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}