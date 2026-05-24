use actix_web::{web, App, HttpServer, HttpResponse, Responder, Error};
use actix_web::middleware::Logger;
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
use std::env;
use r2d2::{Pool, PooledConnection};
use r2d2_sqlite::SqliteConnectionManager;
use uuid::Uuid;

#[derive(Serialize, Deserialize)]
struct Product {
    name: String,
    #[serde(flatten)]
    properties: serde_json::Map<String, serde_json::Value>,
}

#[derive(Serialize, Deserialize)]
struct ProductData {
    name: String,
    data: String,
}

#[derive(Serialize)]
struct SearchResult {
    results: Vec<Product>,
}

struct AppState {
    db_pool: Pool<SqliteConnectionManager>,
}

async fn add_product(data: web::Json<Product>, state: web::Data<AppState>) -> impl Responder {
    let conn = match state.db_pool.get() {
        Ok(conn) => conn,
        Err(_) => return HttpResponse::InternalServerError().body("Database connection error"),
    };

    let product_json = match serde_json::to_string(&data.into_inner()) {
        Ok(json) => json,
        Err(_) => return HttpResponse::BadRequest().body("Invalid product data"),
    };

    match conn.execute(
        "INSERT INTO products (id, name, data) VALUES (?1, ?2, ?3)",
        params![Uuid::new_v4().to_string(), data.name, product_json],
    ) {
        Ok(_) => HttpResponse::Created().finish(),
        Err(_) => HttpResponse::InternalServerError().body("Failed to add product"),
    }
}

async fn download_product(web::Query(info): web::Query<ProductData>, state: web::Data<AppState>) -> impl Responder {
    let conn = match state.db_pool.get() {
        Ok(conn) => conn,
        Err(_) => return HttpResponse::InternalServerError().body("Database connection error"),
    };

    let mut stmt = match conn.prepare("SELECT data FROM products WHERE name = ?1") {
        Ok(stmt) => stmt,
        Err(_) => return HttpResponse::InternalServerError().body("Failed to prepare statement"),
    };

    let product_iter = match stmt.query_map(params![info.name], |row| row.get(0)) {
        Ok(iter) => iter,
        Err(_) => return HttpResponse::InternalServerError().body("Failed to query products"),
    };

    for product in product_iter {
        match product {
            Ok(product) => return HttpResponse::Ok().json(product),
            Err(_) => return HttpResponse::InternalServerError().body("Failed to retrieve product"),
        }
    }

    HttpResponse::NotFound().body("Product not found")
}

async fn upload_product(data: web::Json<ProductData>, state: web::Data<AppState>) -> impl Responder {
    let conn = match state.db_pool.get() {
        Ok(conn) => conn,
        Err(_) => return HttpResponse::InternalServerError().body("Database connection error"),
    };

    match conn.execute(
        "UPDATE products SET data = ?1 WHERE name = ?2",
        params![data.data, data.name],
    ) {
        Ok(_) => HttpResponse::Ok().finish(),
        Err(_) => HttpResponse::InternalServerError().body("Failed to update product"),
    }
}

async fn search_products(web::Query(info): web::Query<ProductData>, state: web::Data<AppState>) -> impl Responder {
    let conn = match state.db_pool.get() {
        Ok(conn) => conn,
        Err(_) => return HttpResponse::InternalServerError().body("Database connection error"),
    };

    let mut stmt = match conn.prepare("SELECT data FROM products WHERE data LIKE ?1") {
        Ok(stmt) => stmt,
        Err(_) => return HttpResponse::InternalServerError().body("Failed to prepare statement"),
    };

    let product_iter = match stmt.query_map(params![format!("%{}%", info.name)], |row| row.get(0)) {
        Ok(iter) => iter,
        Err(_) => return HttpResponse::InternalServerError().body("Failed to query products"),
    };

    let mut results = Vec::new();
    for product in product_iter {
        match product {
            Ok(product) => {
                let product: Product = match serde_json::from_str(&product) {
                    Ok(prod) => prod,
                    Err(_) => return HttpResponse::InternalServerError().body("Failed to parse product data"),
                };
                results.push(product);
            }
            Err(_) => return HttpResponse::InternalServerError().body("Failed to retrieve product"),
        }
    }

    HttpResponse::Ok().json(SearchResult { results })
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    let database_url = env::var("DATABASE_URL").unwrap_or_else(|_| "db.sqlite3".to_string());
    let manager = SqliteConnectionManager::file(database_url);
    let pool = Pool::new(manager).expect("Failed to create pool.");

    {
        let conn = pool.get().expect("Failed to get DB connection");
        conn.execute(
            "CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                data TEXT NOT NULL
            )",
            [],
        ).expect("Failed to create table.");
    }

    let app_state = web::Data::new(AppState {
        db_pool: pool,
    });

    HttpServer::new(move || {
        App::new()
            .wrap(Logger::default())
            .app_data(app_state.clone())
            .route("/add", web::post().to(add_product))
            .route("/download", web::get().to(download_product))
            .route("/upload", web::post().to(upload_product))
            .route("/search", web::get().to(search_products))
    })
    .bind("127.0.0.1:5000")?
    .run()
    .await
}