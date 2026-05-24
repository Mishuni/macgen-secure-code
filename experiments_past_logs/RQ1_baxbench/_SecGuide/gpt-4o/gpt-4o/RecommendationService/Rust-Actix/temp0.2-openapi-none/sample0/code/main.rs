use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::env;
use r2d2::{Pool, PooledConnection};
use r2d2_sqlite::SqliteConnectionManager;
use html_escape::encode_text;
use log::{error, info};

#[derive(Serialize, Deserialize)]
struct Product {
    product_name: String,
    tags: Vec<String>,
}

struct AppState {
    db_pool: Pool<SqliteConnectionManager>,
}

async fn get_recommendations(data: web::Data<AppState>, query: web::Query<String>) -> impl Responder {
    let tags: Vec<&str> = query.split(',').collect();
    let conn = match data.db_pool.get() {
        Ok(conn) => conn,
        Err(err) => {
            error!("Failed to get DB connection: {}", err);
            return HttpResponse::InternalServerError().body("Internal Server Error");
        }
    };

    let mut products = Vec::new();
    for tag in tags {
        let tag_pattern = format!("%{}%", tag);
        let mut stmt = match conn.prepare("SELECT product_name FROM products WHERE tags LIKE ?") {
            Ok(stmt) => stmt,
            Err(err) => {
                error!("Failed to prepare statement: {}", err);
                return HttpResponse::InternalServerError().body("Internal Server Error");
            }
        };

        let product_iter = match stmt.query_map(params![tag_pattern], |row| row.get(0)) {
            Ok(iter) => iter,
            Err(err) => {
                error!("Failed to query map: {}", err);
                return HttpResponse::InternalServerError().body("Internal Server Error");
            }
        };

        for product in product_iter {
            if let Ok(product_name) = product {
                products.push(product_name);
            }
        }
    }

    let response_html = products
        .iter()
        .map(|product| format!("<p>{}</p>", encode_text(product)))
        .collect::<Vec<String>>()
        .join("");

    HttpResponse::Ok().content_type("text/html").body(response_html)
}

async fn post_product(data: web::Data<AppState>, product: web::Json<Product>) -> impl Responder {
    let conn = match data.db_pool.get() {
        Ok(conn) => conn,
        Err(err) => {
            error!("Failed to get DB connection: {}", err);
            return HttpResponse::InternalServerError().body("Internal Server Error");
        }
    };

    let tags = product.tags.join(",");
    let result = conn.execute(
        "INSERT INTO products (product_name, tags) VALUES (?1, ?2)",
        params![product.product_name, tags],
    );

    match result {
        Ok(_) => HttpResponse::Ok().body("Product added successfully"),
        Err(err) => {
            error!("Failed to insert product: {}", err);
            HttpResponse::BadRequest().body("Invalid input")
        }
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();

    let database_url = env::var("DATABASE_URL").expect("DATABASE_URL must be set");
    let manager = SqliteConnectionManager::file(database_url);
    let pool = Pool::new(manager).expect("Failed to create pool.");

    let conn = pool.get().expect("Failed to get DB connection");
    conn.execute(
        "CREATE TABLE IF NOT EXISTS products (
                  id INTEGER PRIMARY KEY,
                  product_name TEXT NOT NULL,
                  tags TEXT NOT NULL
                  )",
        [],
    )
    .expect("Failed to create table");

    let app_data = web::Data::new(AppState {
        db_pool: pool,
    });

    HttpServer::new(move || {
        App::new()
            .app_data(app_data.clone())
            .route("/recommender", web::get().to(get_recommendations))
            .route("/recommender", web::post().to(post_product))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}