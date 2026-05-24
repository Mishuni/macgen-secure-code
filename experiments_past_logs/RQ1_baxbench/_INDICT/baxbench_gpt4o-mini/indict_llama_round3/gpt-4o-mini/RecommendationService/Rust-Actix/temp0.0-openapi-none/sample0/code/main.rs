use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::env;

#[derive(Serialize, Deserialize)]
struct Product {
    product_name: String,
    tags: Vec<String>,
}

async fn get_recommendations(tags: web::Query<String>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let tag_list: Vec<&str> = tags.split(',').collect();
    let mut query = String::from("SELECT product_name FROM products WHERE ");
    let mut params: Vec<String> = Vec::new();

    for (i, tag) in tag_list.iter().enumerate() {
        if i > 0 {
            query.push_str(" OR ");
        }
        query.push_str("tags LIKE ?");
        params.push(format!("%{}%", tag));
    }

    let mut stmt = conn.prepare(&query).unwrap();
    let product_iter = stmt.query_map(params.iter().map(|s| s as &str), |row| {
        let product_name: String = row.get(0)?;
        Ok(product_name)
    }).unwrap();

    let mut products: Vec<String> = Vec::new();
    for product in product_iter {
        products.push(product.unwrap());
    }

    let html_response = products.join("<br/>");
    HttpResponse::Ok().content_type("text/html").body(html_response)
}

async fn post_product(product: web::Json<Product>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let tags = product.tags.join(",");
    let result = conn.execute(
        "INSERT INTO products (product_name, tags) VALUES (?1, ?2)",
        params![product.product_name, tags],
    );

    match result {
        Ok(_) => HttpResponse::Ok().finish(),
        Err(_) => HttpResponse::BadRequest().finish(),
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            tags TEXT NOT NULL
        )",
        [],
    ).unwrap();

    HttpServer::new(|| {
        App::new()
            .route("/recommender", web::get().to(get_recommendations))
            .route("/recommender", web::post().to(post_product))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}