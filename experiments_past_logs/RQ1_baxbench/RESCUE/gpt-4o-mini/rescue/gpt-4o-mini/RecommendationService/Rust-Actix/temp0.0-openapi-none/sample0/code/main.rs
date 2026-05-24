use actix_web::{get, post, web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection};
use serde::{Deserialize, Serialize};
use std::env;

#[derive(Serialize, Deserialize)]
struct Product {
    product_name: String,
    tags: Vec<String>,
}

#[get("/recommender")]
async fn recommend_products(web::Query(tags): web::Query<String>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let tags: Vec<&str> = tags.split(',').collect();
    let mut query = String::from("SELECT product_name FROM products WHERE ");
    let mut conditions: Vec<String> = Vec::new();

    for tag in tags {
        conditions.push(format!("tags LIKE ?"));
    }
    query.push_str(&conditions.join(" OR "));
    
    let mut stmt = conn.prepare(&query).unwrap();
    let mut product_names: Vec<String> = Vec::new();
    
    for tag in tags {
        let like_pattern = format!("%{}%", tag);
        let rows = stmt.query_map(params![like_pattern], |row| {
            row.get(0)
        }).unwrap();
        
        for name in rows {
            if let Ok(name) = name {
                product_names.push(name);
            }
        }
    }

    let response = format!("<html><body><h1>Recommended Products</h1><ul>{}</ul></body></html>",
        product_names.iter().map(|name| format!("<li>{}</li>", name)).collect::<String>());
    
    HttpResponse::Ok().content_type("text/html").body(response)
}

#[post("/recommender")]
async fn post_product(product: web::Json<Product>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            tags TEXT NOT NULL
        )",
        [],
    ).unwrap();

    let tags = product.tags.join(",");
    conn.execute(
        "INSERT INTO products (product_name, tags) VALUES (?1, ?2)",
        params![product.product_name, tags],
    ).unwrap();

    HttpResponse::Ok().body("Product added successfully")
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let _ = env_logger::init();
    HttpServer::new(|| {
        App::new()
            .service(recommend_products)
            .service(post_product)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}