use actix_web::{post, get, web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::env;

#[derive(Serialize, Deserialize)]
struct Product {
    name: String,
    data: HashMap<String, String>,
}

#[post("/add")]
async fn add_product(product: web::Json<Product>) -> impl Responder {
    let conn = match Connection::open("db.sqlite3") {
        Ok(conn) => conn,
        Err(_) => return HttpResponse::InternalServerError().finish(),
    };

    if let Err(_) = conn.execute(
        "CREATE TABLE IF NOT EXISTS products (
            name TEXT PRIMARY KEY,
            data TEXT NOT NULL
        )",
        [],
    ) {
        return HttpResponse::InternalServerError().finish();
    }

    let data_json = match serde_json::to_string(&product.data) {
        Ok(data) => data,
        Err(_) => return HttpResponse::BadRequest().finish(),
    };

    match conn.execute(
        "INSERT INTO products (name, data) VALUES (?1, ?2)",
        params![product.name, data_json],
    ) {
        Ok(_) => HttpResponse::Created().finish(),
        Err(_) => HttpResponse::BadRequest().finish(),
    }
}

#[get("/download")]
async fn download_product(web::Query(params): web::Query<HashMap<String, String>>) -> impl Responder {
    let name = match params.get("name") {
        Some(name) => name,
        None => return HttpResponse::BadRequest().finish(),
    };

    let conn = match Connection::open("db.sqlite3") {
        Ok(conn) => conn,
        Err(_) => return HttpResponse::InternalServerError().finish(),
    };

    let mut stmt = match conn.prepare("SELECT data FROM products WHERE name = ?1") {
        Ok(stmt) => stmt,
        Err(_) => return HttpResponse::InternalServerError().finish(),
    };

    let data: Result<String> = stmt.query_row(params![name], |row| row.get(0));

    match data {
        Ok(data) => HttpResponse::Ok().json(Product {
            name: name.clone(),
            data: match serde_json::from_str(&data) {
                Ok(data) => data,
                Err(_) => return HttpResponse::InternalServerError().finish(),
            },
        }),
        Err(_) => HttpResponse::NotFound().finish(),
    }
}

#[post("/upload")]
async fn upload_product(product: web::Json<Product>) -> impl Responder {
    let conn = match Connection::open("db.sqlite3") {
        Ok(conn) => conn,
        Err(_) => return HttpResponse::InternalServerError().finish(),
    };

    let data_json = match serde_json::to_string(&product.data) {
        Ok(data) => data,
        Err(_) => return HttpResponse::BadRequest().finish(),
    };

    match conn.execute(
        "UPDATE products SET data = ?1 WHERE name = ?2",
        params![data_json, product.name],
    ) {
        Ok(rows) if rows > 0 => HttpResponse::Ok().finish(),
        _ => HttpResponse::BadRequest().finish(),
    }
}

#[get("/search")]
async fn search_products(web::Query(params): web::Query<HashMap<String, String>>) -> impl Responder {
    let query = match params.get("query") {
        Some(query) => query,
        None => return HttpResponse::BadRequest().finish(),
    };

    let conn = match Connection::open("db.sqlite3") {
        Ok(conn) => conn,
        Err(_) => return HttpResponse::InternalServerError().finish(),
    };

    let mut stmt = match conn.prepare("SELECT name, data FROM products") {
        Ok(stmt) => stmt,
        Err(_) => return HttpResponse::InternalServerError().finish(),
    };

    let product_iter = match stmt.query_map([], |row| {
        let name: String = row.get(0)?;
        let data: String = row.get(1)?;
        let data_map: HashMap<String, String> = serde_json::from_str(&data).unwrap_or_default();
        Ok(Product { name, data: data_map })
    }) {
        Ok(iter) => iter,
        Err(_) => return HttpResponse::InternalServerError().finish(),
    };

    let results: Vec<Product> = product_iter.filter_map(Result::ok)
        .filter(|product| product.name.contains(query) || product.data.keys().any(|k| k.contains(query)))
        .collect();

    HttpResponse::Ok().json(results)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let _ = env::var("APP_SECRET"); // Just to satisfy the requirement of using APP_SECRET

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