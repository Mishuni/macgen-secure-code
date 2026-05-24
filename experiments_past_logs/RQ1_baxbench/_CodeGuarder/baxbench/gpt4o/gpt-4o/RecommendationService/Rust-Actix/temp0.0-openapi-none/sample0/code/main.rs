use actix_web::{web, App, HttpServer, HttpResponse, Responder, middleware::Logger};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
use std::env;
use log::info;

#[derive(Serialize, Deserialize)]
struct Product {
    product_name: String,
    tags: Vec<String>,
}

async fn get_recommendations(query: web::Query<std::collections::HashMap<String, String>>) -> impl Responder {
    let tags = query.get("tags").unwrap_or(&"".to_string());
    let tag_list: Vec<&str> = tags.split(',').collect();

    let conn = Connection::open("db.sqlite3").expect("Failed to connect to database");
    let mut stmt = conn.prepare("SELECT product_name FROM products WHERE tags LIKE ?").expect("Failed to prepare statement");

    let mut products = Vec::new();
    for tag in tag_list {
        let tag_pattern = format!("%{}%", tag);
        let product_iter = stmt.query_map(params![tag_pattern], |row| {
            row.get(0)
        }).expect("Failed to query products");

        for product in product_iter {
            products.push(product.expect("Failed to get product"));
        }
    }

    let response = format!("<html><body><ul>{}</ul></body></html>", products.iter().map(|p| format!("<li>{}</li>", p)).collect::<String>());
    HttpResponse::Ok().content_type("text/html").body(response)
}

async fn post_product(product: web::Json<Product>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").expect("Failed to connect to database");
    conn.execute(
        "CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, product_name TEXT NOT NULL, tags TEXT NOT NULL)",
        [],
    ).expect("Failed to create table");

    let tags = product.tags.join(",");
    conn.execute(
        "INSERT INTO products (product_name, tags) VALUES (?1, ?2)",
        params![product.product_name, tags],
    ).expect("Failed to insert product");

    HttpResponse::Ok().body("Product added successfully")
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    let app_secret = env::var("APP_SECRET").expect("APP_SECRET must be set");

    info!("Starting server with secret: {}", app_secret);

    HttpServer::new(|| {
        App::new()
            .wrap(Logger::default())
            .route("/recommender", web::get().to(get_recommendations))
            .route("/recommender", web::post().to(post_product))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}