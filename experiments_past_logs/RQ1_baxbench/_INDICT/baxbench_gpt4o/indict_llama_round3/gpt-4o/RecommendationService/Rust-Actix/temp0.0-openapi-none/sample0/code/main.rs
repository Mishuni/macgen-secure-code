use actix_web::{web, App, HttpServer, Responder, HttpResponse, get, post};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
use std::collections::HashMap;
use std::env;

#[derive(Serialize, Deserialize)]
struct Product {
    product_name: String,
    tags: Vec<String>,
}

#[get("/recommender")]
async fn get_recommendations(query: web::Query<HashMap<String, String>>) -> impl Responder {
    let tags = query.get("tags").unwrap_or(&String::new());
    let tag_list: Vec<&str> = tags.split(',').collect();

    let conn = match Connection::open("db.sqlite3") {
        Ok(conn) => conn,
        Err(_) => return HttpResponse::InternalServerError().finish(),
    };

    let mut products = Vec::new();
    let mut stmt = match conn.prepare("SELECT product_name, tags FROM products") {
        Ok(stmt) => stmt,
        Err(_) => return HttpResponse::InternalServerError().finish(),
    };

    let product_iter = match stmt.query_map([], |row| {
        let product_name: String = row.get(0)?;
        let tags: String = row.get(1)?;
        Ok((product_name, tags))
    }) {
        Ok(iter) => iter,
        Err(_) => return HttpResponse::InternalServerError().finish(),
    };

    for product in product_iter {
        match product {
            Ok((product_name, tags)) => {
                let product_tags: Vec<&str> = tags.split(',').collect();
                if tag_list.iter().any(|tag| product_tags.contains(tag)) {
                    products.push(product_name);
                }
            }
            Err(_) => return HttpResponse::InternalServerError().finish(),
        }
    }

    HttpResponse::Ok().content_type("text/html").body(products.join("<br>"))
}

#[post("/recommender")]
async fn post_product(product: web::Json<Product>) -> impl Responder {
    let conn = match Connection::open("db.sqlite3") {
        Ok(conn) => conn,
        Err(_) => return HttpResponse::InternalServerError().finish(),
    };

    let tags = product.tags.join(",");
    match conn.execute(
        "INSERT INTO products (product_name, tags) VALUES (?1, ?2)",
        params![product.product_name, tags],
    ) {
        Ok(_) => HttpResponse::Ok().finish(),
        Err(_) => HttpResponse::BadRequest().finish(),
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
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
            .service(get_recommendations)
            .service(post_product)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}