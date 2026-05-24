use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection};
use serde::{Deserialize, Serialize};
use std::env;

#[derive(Serialize, Deserialize)]
struct Product {
    product_name: String,
    tags: Vec<String>,
}

fn escape_html(input: &str) -> String {
    let mut escaped = String::new();
    for c in input.chars() {
        match c {
            '&' => escaped.push_str("&amp;"),
            '<' => escaped.push_str("&lt;"),
            '>' => escaped.push_str("&gt;"),
            '"' => escaped.push_str("&quot;"),
            '\'' => escaped.push_str("&apos;"),
            _ => escaped.push(c),
        }
    }
    escaped
}

fn validate_tags(tags: &str) -> Result<Vec<String>, &'static str> {
    let tag_list: Vec<&str> = tags.split(',').collect();
    if tag_list.is_empty() {
        return Err("No tags provided");
    }
    // Additional validation can be added here (e.g., length, format)
    Ok(tag_list.iter().map(|&tag| tag.trim().to_string()).collect())
}

async fn get_recommendations(tags: web::Query<String>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").expect("Failed to open database");
    
    let tag_list = match validate_tags(&tags) {
        Ok(tags) => tags,
        Err(err) => return HttpResponse::BadRequest().body(err),
    };

    let mut query = String::from("SELECT product_name FROM products WHERE");
    let mut params: Vec<String> = Vec::new();

    for (i, tag) in tag_list.iter().enumerate() {
        if i > 0 {
            query.push_str(" OR");
        }
        query.push_str(" tags LIKE ?");
        params.push(format!("%{}%", tag));
    }

    let mut stmt = conn.prepare(&query).expect("Failed to prepare statement");
    let product_iter = stmt.query_map(params.iter().map(|s| s as &str), |row| {
        let product_name: String = row.get(0)?;
        Ok(product_name)
    }).expect("Failed to execute query");

    let mut products = String::from("<html><body><h1>Recommended Products</h1><ul>");
    for product in product_iter {
        products.push_str(&format!("<li>{}</li>", escape_html(&product.expect("Failed to get product name"))));
    }
    products.push_str("</ul></body></html>");

    HttpResponse::Ok().content_type("text/html").body(products)
}

async fn post_product(product: web::Json<Product>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").expect("Failed to open database");
    conn.execute(
        "INSERT INTO products (product_name, tags) VALUES (?1, ?2)",
        params![product.product_name, product.tags.join(",")],
    ).expect("Failed to insert product");

    HttpResponse::Ok().finish()
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let conn = Connection::open("db.sqlite3").expect("Failed to open database");
    conn.execute(
        "CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            tags TEXT NOT NULL
        )",
        [],
    ).expect("Failed to create table");

    HttpServer::new(|| {
        App::new()
            .route("/recommender", web::get().to(get_recommendations))
            .route("/recommender", web::post().to(post_product))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}