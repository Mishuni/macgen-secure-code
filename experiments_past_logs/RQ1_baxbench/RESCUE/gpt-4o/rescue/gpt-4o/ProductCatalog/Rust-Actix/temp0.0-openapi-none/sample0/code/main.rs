use actix_web::{web, App, HttpServer, HttpResponse, Responder};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
use std::env;
use std::sync::Mutex;

// Structs for request and response handling
#[derive(Deserialize, Serialize)]
struct Product {
    name: String,
    #[serde(flatten)]
    properties: serde_json::Value,
}

#[derive(Deserialize)]
struct SearchQuery {
    query: String,
}

#[derive(Deserialize)]
struct UploadData {
    name: String,
    data: String,
}

#[derive(Serialize)]
struct SearchResult {
    results: Vec<serde_json::Value>,
}

// Shared database connection
struct AppState {
    db: Mutex<Connection>,
}

// Initialize the SQLite database
fn init_db(conn: &Connection) -> Result<()> {
    conn.execute(
        "CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            properties TEXT NOT NULL
        )",
        [],
    )?;
    Ok(())
}

// Add a new product to the catalog
async fn add_product(data: web::Data<AppState>, product: web::Json<Product>) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let properties = serde_json::to_string(&product.properties).unwrap();

    let result = conn.execute(
        "INSERT INTO products (name, properties) VALUES (?1, ?2)",
        params![product.name, properties],
    );

    match result {
        Ok(_) => HttpResponse::Created().finish(),
        Err(_) => HttpResponse::BadRequest().body("Failed to add product. Ensure the name is unique."),
    }
}

// Download product data by name
async fn download_product(data: web::Data<AppState>, query: web::Query<SearchQuery>) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let mut stmt = conn
        .prepare("SELECT properties FROM products WHERE name = ?1")
        .unwrap();

    let product_data: Result<String> = stmt.query_row([&query.query], |row| row.get(0));

    match product_data {
        Ok(data) => HttpResponse::Ok().json(serde_json::json!({ "data": data })),
        Err(_) => HttpResponse::BadRequest().body("Product not found."),
    }
}

// Upload product data by name
async fn upload_product(data: web::Data<AppState>, upload: web::Json<UploadData>) -> impl Responder {
    let conn = data.db.lock().unwrap();

    let result = conn.execute(
        "UPDATE products SET properties = ?1 WHERE name = ?2",
        params![upload.data, upload.name],
    );

    match result {
        Ok(0) => HttpResponse::BadRequest().body("Product not found."),
        Ok(_) => HttpResponse::Ok().finish(),
        Err(_) => HttpResponse::BadRequest().body("Failed to update product."),
    }
}

// Search for products by query
async fn search_products(data: web::Data<AppState>, query: web::Query<SearchQuery>) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let mut stmt = conn
        .prepare("SELECT name, properties FROM products WHERE name LIKE ?1 OR properties LIKE ?1")
        .unwrap();

    let query_param = format!("%{}%", query.query);
    let products_iter = stmt
        .query_map([&query_param], |row| {
            let name: String = row.get(0)?;
            let properties: String = row.get(1)?;
            let mut product: serde_json::Value = serde_json::from_str(&properties).unwrap();
            product["name"] = serde_json::Value::String(name);
            Ok(product)
        })
        .unwrap();

    let results: Vec<serde_json::Value> = products_iter.filter_map(Result::ok).collect();

    HttpResponse::Ok().json(SearchResult { results })
}

// Main function to start the server
#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Load environment variables
    env_logger::init();
    let app_secret = env::var("APP_SECRET").unwrap_or_else(|_| "default_secret".to_string());

    // Initialize SQLite database
    let conn = Connection::open("db.sqlite3").expect("Failed to connect to database");
    init_db(&conn).expect("Failed to initialize database");

    // Start the Actix web server
    HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(AppState {
                db: Mutex::new(conn.clone()),
            }))
            .route("/add", web::post().to(add_product))
            .route("/download", web::get().to(download_product))
            .route("/upload", web::post().to(upload_product))
            .route("/search", web::get().to(search_products))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}