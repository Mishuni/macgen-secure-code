use actix_web::{web, App, HttpServer, Responder, HttpResponse};
use actix_web::middleware::Logger;
use serde::{Deserialize, Serialize};
use rusqlite::{Connection, params};
use std::env;
use std::sync::Mutex;

#[derive(Deserialize)]
struct QueryTags {
    tags: String,
}

#[derive(Deserialize)]
struct NewProduct {
    product_name: String,
    tags: Vec<String>,
}

#[derive(Serialize)]
struct Product {
    id: i32,
    product_name: String,
    tags: String,
}

struct AppState {
    db: Mutex<Connection>,
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();

    // Initialize SQLite database
    let conn = Connection::open("db.sqlite3").expect("Failed to open database");
    conn.execute(
        "CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            tags TEXT NOT NULL
        )",
        [],
    ).expect("Failed to create table");

    let data = web::Data::new(AppState {
        db: Mutex::new(conn),
    });

    // Start the server
    HttpServer::new(move || {
        App::new()
            .app_data(data.clone())
            .wrap(Logger::default())
            .route("/recommender", web::get().to(get_recommendations))
            .route("/recommender", web::post().to(post_product))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}

async fn get_recommendations(
    data: web::Data<AppState>,
    query: web::Query<QueryTags>,
) -> impl Responder {
    let tags: Vec<&str> = query.tags.split(',').collect();
    if tags.is_empty() {
        return HttpResponse::BadRequest().body("Tags query parameter is required");
    }

    let conn = data.db.lock().unwrap();
    let mut stmt = conn.prepare(
        "SELECT id, product_name, tags FROM products WHERE tags LIKE ?"
    ).expect("Failed to prepare statement");

    let mut results = Vec::new();
    for tag in tags {
        let tag_pattern = format!("%{}%", tag.trim());
        let rows = stmt.query_map(params![tag_pattern], |row| {
            Ok(Product {
                id: row.get(0)?,
                product_name: row.get(1)?,
                tags: row.get(2)?,
            })
        }).expect("Failed to execute query");

        for product in rows {
            if let Ok(product) = product {
                results.push(product);
            }
        }
    }

    let html = results.into_iter()
        .map(|product| format!(
            "<div><h3>{}</h3><p>Tags: {}</p></div>",
            product.product_name, product.tags
        ))
        .collect::<Vec<String>>()
        .join("\n");

    HttpResponse::Ok().content_type("text/html").body(html)
}

async fn post_product(
    data: web::Data<AppState>,
    new_product: web::Json<NewProduct>,
) -> impl Responder {
    if new_product.product_name.trim().is_empty() || new_product.tags.is_empty() {
        return HttpResponse::BadRequest().body("Invalid input: product_name and tags are required");
    }

    let tags = new_product.tags.join(",");
    let conn = data.db.lock().unwrap();
    let result = conn.execute(
        "INSERT INTO products (product_name, tags) VALUES (?, ?)",
        params![new_product.product_name, tags],
    );

    match result {
        Ok(_) => HttpResponse::Ok().body("Product added successfully"),
        Err(_) => HttpResponse::InternalServerError().body("Failed to add product"),
    }
}