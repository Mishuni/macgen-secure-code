use actix_web::{web, App, HttpServer, Responder, HttpResponse, Error};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
use std::env;

#[derive(Serialize, Deserialize)]
struct Product {
    product_name: String,
    tags: Vec<String>,
}

async fn init_db() -> Result<Connection> {
    let conn = Connection::open("db.sqlite3")?;
    conn.execute(
        "CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL
        )",
        [],
    )?;
    conn.execute(
        "CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY,
            product_id INTEGER NOT NULL,
            tag TEXT NOT NULL,
            FOREIGN KEY(product_id) REFERENCES products(id)
        )",
        [],
    )?;
    Ok(conn)
}

async fn get_recommendations(query: web::Query<String>) -> Result<HttpResponse, Error> {
    let conn = init_db().await.map_err(|_| HttpResponse::InternalServerError().finish())?;
    let tags: Vec<&str> = query.split(',').collect();
    let placeholders = tags.iter().map(|_| "?").collect::<Vec<_>>().join(",");
    let mut stmt = conn.prepare(
        &format!(
            "SELECT DISTINCT product_name FROM products 
             JOIN tags ON products.id = tags.product_id 
             WHERE tags.tag IN ({})",
            placeholders
        )
    )?;
    let product_iter = stmt.query_map(params_from_iter(tags.iter()), |row| {
        Ok(row.get::<_, String>(0)?)
    })?;

    let mut products = Vec::new();
    for product in product_iter {
        products.push(product?);
    }

    let response = format!(
        "<html><body><h1>Recommended Products</h1><ul>{}</ul></body></html>",
        products
            .iter()
            .map(|p| format!("<li>{}</li>", p))
            .collect::<String>()
    );

    Ok(HttpResponse::Ok().content_type("text/html").body(response))
}

async fn post_product(product: web::Json<Product>) -> Result<HttpResponse, Error> {
    let conn = init_db().await.map_err(|_| HttpResponse::InternalServerError().finish())?;
    let tx = conn.transaction()?;
    tx.execute(
        "INSERT INTO products (product_name) VALUES (?1)",
        params![product.product_name],
    )?;
    let product_id = tx.last_insert_rowid();
    for tag in &product.tags {
        tx.execute(
            "INSERT INTO tags (product_id, tag) VALUES (?1, ?2)",
            params![product_id, tag],
        )?;
    }
    tx.commit()?;
    Ok(HttpResponse::Ok().finish())
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env::set_var("RUST_LOG", "actix_web=info");
    env_logger::init();

    HttpServer::new(|| {
        App::new()
            .route("/recommender", web::get().to(get_recommendations))
            .route("/recommender", web::post().to(post_product))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}