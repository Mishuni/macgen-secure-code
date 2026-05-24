use actix_web::{post, get, web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::env;
use regex::Regex;

#[derive(Serialize, Deserialize)]
struct Product {
    name: String,
    data: HashMap<String, String>,
}

fn validate_product_name(name: &str) -> bool {
    let re = Regex::new(r"^[a-zA-Z0-9\s]+$").unwrap();
    re.is_match(name) && name.len() <= 100
}

#[post("/add")]
async fn add_product(product: web::Json<Product>) -> impl Responder {
    if !validate_product_name(&product.name) {
        return HttpResponse::BadRequest().finish();
    }

    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS products (
            name TEXT PRIMARY KEY,
            data TEXT NOT NULL
        )",
        [],
    ).unwrap();

    let data = serde_json::to_string(&product.data).unwrap();
    match conn.execute(
        "INSERT INTO products (name, data) VALUES (?1, ?2)",
        params![product.name, data],
    ) {
        Ok(_) => HttpResponse::Created().finish(),
        Err(_) => HttpResponse::BadRequest().finish(),
    }
}

#[get("/download")]
async fn download_product(web::Query(name): web::Query<HashMap<String, String>>) -> impl Responder {
    let product_name = name.get("name").unwrap();
    if !validate_product_name(product_name) {
        return HttpResponse::BadRequest().finish();
    }

    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare("SELECT data FROM products WHERE name = ?1").unwrap();
    let data: Result<String> = stmt.query_row(params![product_name], |row| row.get(0));

    match data {
        Ok(data) => HttpResponse::Ok().json(Product {
            name: product_name.clone(),
            data: serde_json::from_str(&data).unwrap(),
        }),
        Err(_) => HttpResponse::NotFound().finish(),
    }
}

#[post("/upload")]
async fn upload_product(product: web::Json<Product>) -> impl Responder {
    if !validate_product_name(&product.name) {
        return HttpResponse::BadRequest().finish();
    }

    let conn = Connection::open("db.sqlite3").unwrap();
    let data = serde_json::to_string(&product.data).unwrap();
    match conn.execute(
        "UPDATE products SET data = ?1 WHERE name = ?2",
        params![data, product.name],
    ) {
        Ok(rows) if rows > 0 => HttpResponse::Ok().finish(),
        _ => HttpResponse::BadRequest().finish(),
    }
}

#[get("/search")]
async fn search_products(web::Query(query): web::Query<HashMap<String, String>>) -> impl Responder {
    let search_query = query.get("query").unwrap();
    if search_query.is_empty() {
        return HttpResponse::BadRequest().finish();
    }

    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare("SELECT name, data FROM products").unwrap();
    let product_iter = stmt.query_map([], |row| {
        let name: String = row.get(0)?;
        let data: String = row.get(1)?;
        let data_map: HashMap<String, String> = serde_json::from_str(&data).unwrap();
        Ok(Product { name, data: data_map })
    }).unwrap();

    let results: Vec<Product> = product_iter.filter_map(|product| {
        let product = product.ok()?;
        if product.name.contains(search_query) || product.data.keys().any(|k| k.contains(search_query)) {
            Some(product)
        } else {
            None
        }
    }).collect();

    HttpResponse::Ok().json(results)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let _ = env::var("APP_SECRET").unwrap_or_else(|_| "default_secret".to_string());
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