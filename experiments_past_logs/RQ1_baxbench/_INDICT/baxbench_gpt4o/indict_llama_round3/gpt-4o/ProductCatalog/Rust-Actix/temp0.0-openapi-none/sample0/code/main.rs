use actix_web::{web, App, HttpServer, HttpResponse, Responder, Error};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
use std::env;
use std::sync::Mutex;
use log::error;

#[derive(Serialize, Deserialize)]
struct Product {
    name: String,
    #[serde(flatten)]
    properties: std::collections::HashMap<String, String>,
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

struct AppState {
    db: Mutex<Connection>,
}

async fn add_product(data: web::Json<Product>, state: web::Data<AppState>) -> impl Responder {
    let conn = state.db.lock().unwrap();
    let product_json = match serde_json::to_string(&data.into_inner()) {
        Ok(json) => json,
        Err(_) => return HttpResponse::BadRequest().body("Invalid product data"),
    };

    match conn.execute(
        "INSERT INTO products (name, data) VALUES (?1, ?2)",
        params![data.name, product_json],
    ) {
        Ok(_) => HttpResponse::Created().finish(),
        Err(err) => {
            error!("Failed to add product: {}", err);
            HttpResponse::BadRequest().body("Failed to add product")
        },
    }
}

async fn download_product(web::Query(info): web::Query<std::collections::HashMap<String, String>>, state: web::Data<AppState>) -> impl Responder {
    let conn = state.db.lock().unwrap();
    let name = match info.get("name") {
        Some(name) => name,
        None => return HttpResponse::BadRequest().body("Missing product name"),
    };

    let mut stmt = match conn.prepare("SELECT data FROM products WHERE name = ?1") {
        Ok(stmt) => stmt,
        Err(err) => {
            error!("Failed to prepare statement: {}", err);
            return HttpResponse::InternalServerError().finish();
        },
    };

    let product_iter = match stmt.query_map(params![name], |row| row.get(0)) {
        Ok(iter) => iter,
        Err(err) => {
            error!("Failed to query product: {}", err);
            return HttpResponse::InternalServerError().finish();
        },
    };

    for product in product_iter {
        match product {
            Ok(data) => return HttpResponse::Ok().json(ProductData {
                name: name.clone(),
                data,
            }),
            Err(err) => {
                error!("Failed to get product data: {}", err);
                return HttpResponse::InternalServerError().finish();
            },
        }
    }

    HttpResponse::BadRequest().body("Product not found")
}

async fn upload_product(data: web::Json<ProductData>, state: web::Data<AppState>) -> impl Responder {
    let conn = state.db.lock().unwrap();

    match conn.execute(
        "UPDATE products SET data = ?1 WHERE name = ?2",
        params![data.data, data.name],
    ) {
        Ok(_) => HttpResponse::Ok().finish(),
        Err(err) => {
            error!("Failed to update product: {}", err);
            HttpResponse::BadRequest().body("Failed to update product")
        },
    }
}

async fn search_products(web::Query(info): web::Query<std::collections::HashMap<String, String>>, state: web::Data<AppState>) -> impl Responder {
    let conn = state.db.lock().unwrap();
    let query = match info.get("query") {
        Some(query) => query,
        None => return HttpResponse::BadRequest().body("Missing search query"),
    };

    let mut stmt = match conn.prepare("SELECT data FROM products WHERE data LIKE ?1") {
        Ok(stmt) => stmt,
        Err(err) => {
            error!("Failed to prepare statement: {}", err);
            return HttpResponse::InternalServerError().finish();
        },
    };

    let product_iter = match stmt.query_map(params![format!("%{}%", query)], |row| row.get(0)) {
        Ok(iter) => iter,
        Err(err) => {
            error!("Failed to query products: {}", err);
            return HttpResponse::InternalServerError().finish();
        },
    };

    let mut results = Vec::new();
    for product in product_iter {
        match product {
            Ok(product_data) => {
                match serde_json::from_str::<Product>(&product_data) {
                    Ok(product) => results.push(product),
                    Err(err) => {
                        error!("Failed to deserialize product data: {}", err);
                        return HttpResponse::InternalServerError().finish();
                    },
                }
            },
            Err(err) => {
                error!("Failed to get product data: {}", err);
                return HttpResponse::InternalServerError().finish();
            },
        }
    }

    HttpResponse::Ok().json(SearchResult { results })
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    let database_url = "db.sqlite3";
    let conn = Connection::open(database_url).unwrap();

    conn.execute(
        "CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            data TEXT NOT NULL
        )",
        [],
    ).unwrap();

    let app_state = web::Data::new(AppState {
        db: Mutex::new(conn),
    });

    HttpServer::new(move || {
        App::new()
            .app_data(app_state.clone())
            .route("/add", web::post().to(add_product))
            .route("/download", web::get().to(download_product))
            .route("/upload", web::post().to(upload_product))
            .route("/search", web::get().to(search_products))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}