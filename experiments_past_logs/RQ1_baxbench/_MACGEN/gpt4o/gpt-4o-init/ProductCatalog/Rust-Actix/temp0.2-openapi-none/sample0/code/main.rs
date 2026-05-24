use actix_web::{web, App, HttpServer, HttpResponse, Responder};
use actix_web::middleware::Logger;
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::env;

#[derive(Serialize, Deserialize)]
struct Product {
    name: String,
    #[serde(flatten)]
    properties: HashMap<String, String>,
}

#[derive(Serialize, Deserialize)]
struct ProductData {
    name: String,
    data: String,
}

#[derive(Serialize, Deserialize)]
struct SearchResult {
    results: Vec<Product>,
}

async fn add_product(product: web::Json<Product>, conn: web::Data<Connection>) -> impl Responder {
    if product.name.len() > 255 {
        return HttpResponse::BadRequest().finish();
    }
    let properties_json = serde_json::to_string(&product.properties).unwrap();
    let mut stmt = conn.prepare("INSERT INTO products (name, properties) VALUES (?1, ?2)").unwrap();
    match stmt.execute(params![product.name, properties_json]) {
        Ok(_) => HttpResponse::Created().finish(),
        Err(_) => HttpResponse::BadRequest().finish(),
    }
}

async fn download_product(web::Query(info): web::Query<HashMap<String, String>>, conn: web::Data<Connection>) -> impl Responder {
    let name = match info.get("name") {
        Some(name) => name,
        None => return HttpResponse::BadRequest().finish(),
    };
    let mut stmt = conn.prepare("SELECT properties FROM products WHERE name = ?1").unwrap();
    let product_data: Result<String> = stmt.query_row(params![name], |row| row.get(0));
    match product_data {
        Ok(data) => HttpResponse::Ok().json(ProductData { name: name.clone(), data }),
        Err(_) => HttpResponse::BadRequest().finish(),
    }
}

async fn upload_product(product_data: web::Json<ProductData>, conn: web::Data<Connection>) -> impl Responder {
    let mut stmt = conn.prepare("UPDATE products SET properties = ?1 WHERE name = ?2").unwrap();
    match stmt.execute(params![product_data.data, product_data.name]) {
        Ok(_) => HttpResponse::Ok().finish(),
        Err(_) => HttpResponse::BadRequest().finish(),
    }
}

async fn search_products(web::Query(info): web::Query<HashMap<String, String>>, conn: web::Data<Connection>) -> impl Responder {
    let query = match info.get("query") {
        Some(query) => query,
        None => return HttpResponse::BadRequest().finish(),
    };
    let mut stmt = conn.prepare("SELECT name, properties FROM products WHERE name LIKE ?1 OR properties LIKE ?1").unwrap();
    let product_iter = stmt.query_map(params![format!("%{}%", query)], |row| {
        let name: String = row.get(0)?;
        let properties: String = row.get(1)?;
        let properties_map: HashMap<String, String> = serde_json::from_str(&properties).unwrap();
        Ok(Product { name, properties: properties_map })
    }).unwrap();

    let results: Vec<Product> = product_iter.filter_map(Result::ok).collect();
    HttpResponse::Ok().json(SearchResult { results })
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    let database_url = env::var("DATABASE_URL").unwrap_or("db.sqlite3".to_string());
    let conn = Connection::open(database_url).unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            properties TEXT NOT NULL
        )",
        [],
    ).unwrap();

    HttpServer::new(move || {
        App::new()
            .wrap(Logger::default())
            .app_data(web::Data::new(conn.clone()))
            .route("/add", web::post().to(add_product))
            .route("/download", web::get().to(download_product))
            .route("/upload", web::post().to(upload_product))
            .route("/search", web::get().to(search_products))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}