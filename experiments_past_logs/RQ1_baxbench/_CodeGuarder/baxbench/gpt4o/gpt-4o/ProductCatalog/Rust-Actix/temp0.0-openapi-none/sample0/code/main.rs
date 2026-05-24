use actix_web::{web, App, HttpServer, HttpResponse, Responder, Error};
use actix_web::middleware::Logger;
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
use std::env;
use std::sync::Mutex;
use log::info;

#[derive(Serialize, Deserialize)]
struct Product {
    name: String,
    #[serde(flatten)]
    properties: std::collections::HashMap<String, String>,
}

struct AppState {
    db: Mutex<Connection>,
}

async fn add_product(data: web::Data<AppState>, product: web::Json<Product>) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let tx = conn.transaction().unwrap();

    let product_name = &product.name;
    let product_data = serde_json::to_string(&product.properties).unwrap();

    match tx.execute(
        "INSERT INTO products (name, data) VALUES (?1, ?2)",
        params![product_name, product_data],
    ) {
        Ok(_) => {
            tx.commit().unwrap();
            HttpResponse::Created().finish()
        }
        Err(_) => HttpResponse::BadRequest().finish(),
    }
}

async fn download_product(data: web::Data<AppState>, query: web::Query<std::collections::HashMap<String, String>>) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let product_name = query.get("name").unwrap_or(&String::new());

    let mut stmt = conn.prepare("SELECT data FROM products WHERE name = ?1").unwrap();
    let product_data: Result<String> = stmt.query_row(params![product_name], |row| row.get(0));

    match product_data {
        Ok(data) => HttpResponse::Ok().json(serde_json::json!({ "data": data })),
        Err(_) => HttpResponse::BadRequest().finish(),
    }
}

async fn upload_product(data: web::Data<AppState>, product: web::Json<Product>) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let tx = conn.transaction().unwrap();

    let product_name = &product.name;
    let product_data = &product.properties.get("data").unwrap_or(&String::new());

    match tx.execute(
        "UPDATE products SET data = ?1 WHERE name = ?2",
        params![product_data, product_name],
    ) {
        Ok(_) => {
            tx.commit().unwrap();
            HttpResponse::Ok().finish()
        }
        Err(_) => HttpResponse::BadRequest().finish(),
    }
}

async fn search_products(data: web::Data<AppState>, query: web::Query<std::collections::HashMap<String, String>>) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let search_query = query.get("query").unwrap_or(&String::new());

    let mut stmt = conn.prepare("SELECT name, data FROM products WHERE name LIKE ?1 OR data LIKE ?1").unwrap();
    let product_iter = stmt.query_map(params![format!("%{}%", search_query)], |row| {
        let name: String = row.get(0)?;
        let data: String = row.get(1)?;
        let properties: std::collections::HashMap<String, String> = serde_json::from_str(&data).unwrap();
        Ok(Product { name, properties })
    }).unwrap();

    let mut results = Vec::new();
    for product in product_iter {
        if let Ok(product) = product {
            results.push(product);
        }
    }

    HttpResponse::Ok().json(serde_json::json!({ "results": results }))
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
            .wrap(Logger::default())
            .route("/add", web::post().to(add_product))
            .route("/download", web::get().to(download_product))
            .route("/upload", web::post().to(upload_product))
            .route("/search", web::get().to(search_products))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}