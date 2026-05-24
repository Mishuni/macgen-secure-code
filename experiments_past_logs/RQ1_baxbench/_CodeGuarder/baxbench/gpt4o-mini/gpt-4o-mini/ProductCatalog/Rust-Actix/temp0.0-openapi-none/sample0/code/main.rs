use actix_web::{web, App, HttpServer, HttpResponse, Responder};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::env;
use log::{info, error};

#[derive(Serialize, Deserialize)]
struct Product {
    name: String,
    data: serde_json::Value, // Allows for unstructured properties
}

#[derive(Serialize, Deserialize)]
struct SearchQuery {
    query: String,
}

#[derive(Serialize)]
struct SearchResults {
    results: Vec<Product>,
}

#[derive(Serialize)]
struct UploadResponse {
    message: String,
}

#[derive(Serialize)]
struct DownloadResponse {
    data: String,
}

async fn add_product(product: web::Json<Product>) -> impl Responder {
    let conn = establish_connection();
    match conn.execute(
        "INSERT INTO products (name, data) VALUES (?1, ?2)",
        params![product.name, product.data.to_string()],
    ) {
        Ok(_) => {
            info!("Product added: {}", product.name);
            HttpResponse::Created().finish()
        }
        Err(err) => {
            error!("Failed to add product: {}", err);
            HttpResponse::BadRequest().finish()
        }
    }
}

async fn download_product(web::Query(name): web::Query<String>) -> impl Responder {
    let conn = establish_connection();
    let mut stmt = conn.prepare("SELECT data FROM products WHERE name = ?1").unwrap();
    let data: Result<String> = stmt.query_row(params![name], |row| row.get(0));

    match data {
        Ok(data) => {
            info!("Downloaded product data for: {}", name);
            HttpResponse::Ok().json(DownloadResponse { data })
        }
        Err(err) => {
            error!("Failed to download product: {}", err);
            HttpResponse::BadRequest().finish()
        }
    }
}

async fn upload_product(product: web::Json<Product>) -> impl Responder {
    let conn = establish_connection();
    match conn.execute(
        "REPLACE INTO products (name, data) VALUES (?1, ?2)",
        params![product.name, product.data.to_string()],
    ) {
        Ok(_) => {
            info!("Product updated: {}", product.name);
            HttpResponse::Ok().json(UploadResponse {
                message: "Product updated successfully".to_string(),
            })
        }
        Err(err) => {
            error!("Failed to upload product: {}", err);
            HttpResponse::BadRequest().finish()
        }
    }
}

async fn search_products(web::Query(query): web::Query<SearchQuery>) -> impl Responder {
    let conn = establish_connection();
    let mut stmt = conn.prepare("SELECT name, data FROM products WHERE name LIKE ?1 OR data LIKE ?1")?;
    let search_pattern = format!("%{}%", query.query);
    let product_iter = stmt.query_map(params![search_pattern], |row| {
        Ok(Product {
            name: row.get(0)?,
            data: serde_json::from_str(&row.get::<_, String>(1)?).unwrap(),
        })
    }).unwrap();

    let results: Vec<Product> = product_iter.filter_map(Result::ok).collect();
    HttpResponse::Ok().json(SearchResults { results })
}

fn establish_connection() -> Connection {
    let db_path = "db.sqlite3";
    Connection::open(db_path).expect("Failed to connect to the database")
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    let conn = establish_connection();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            data TEXT NOT NULL
        )",
        [],
    ).expect("Failed to create table");

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