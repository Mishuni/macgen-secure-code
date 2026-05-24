use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::env;

#[derive(Serialize, Deserialize)]
struct Product {
    product_name: String,
    tags: Vec<String>,
}

async fn add_product(product: web::Json<Product>) -> impl Responder {
    if product.product_name.is_empty() || product.tags.is_empty() {
        return HttpResponse::BadRequest().finish();
    }

    let conn = Connection::open("db.sqlite3").unwrap_or_else(|_| {
        panic!("Failed to open database connection");
    });
    
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

    HttpResponse::Ok().finish()
}

async fn get_products(tags: web::Query<HashMap<String, String>>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap_or_else(|_| {
        panic!("Failed to open database connection");
    });

    let tags_query = match tags.get("tags") {
        Some(t) => t,
        None => return HttpResponse::BadRequest().finish(),
    };

    let tags_vec: Vec<&str> = tags_query.split(',').collect();
    
    let mut query = String::from("SELECT product_name, tags FROM products WHERE ");
    let mut params: Vec<String> = Vec::new();
    
    for (i, tag) in tags_vec.iter().enumerate() {
        if i > 0 {
            query.push_str(" OR ");
        }
        query.push_str("tags LIKE ?");
        params.push(format!("%{}%", tag));
    }

    let mut stmt = conn.prepare(&query).unwrap();
    let product_iter = stmt.query_map(params.iter().map(|s| s as &dyn rusqlite::ToSql), |row| {
        let product_name: String = row.get(0)?;
        let tags: String = row.get(1)?;
        Ok(format!("<div><h2>{}</h2><p>Tags: {}</p></div>", product_name, tags))
    }).unwrap();

    let mut response = String::from("<html><body>");
    for product in product_iter {
        response.push_str(&product.unwrap());
    }
    response.push_str("</body></html>");

    HttpResponse::Ok().content_type("text/html").body(response)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let _ = env::var("APP_SECRET").unwrap_or_else(|_| "default_secret".to_string());
    
    HttpServer::new(|| {
        App::new()
            .route("/recommender", web::post().to(add_product))
            .route("/recommender", web::get().to(get_products))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}