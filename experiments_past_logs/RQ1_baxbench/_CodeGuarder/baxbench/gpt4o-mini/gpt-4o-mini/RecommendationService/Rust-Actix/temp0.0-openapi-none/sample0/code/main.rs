use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::env;
use std::sync::Mutex;
use log::{info, error};

#[derive(Serialize, Deserialize)]
struct Product {
    product_name: String,
    tags: Vec<String>,
}

struct AppState {
    db: Mutex<Connection>,
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    let database_url = "db.sqlite3";
    let conn = Connection::open(database_url).expect("Failed to open database");
    conn.execute(
        "CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            tags TEXT NOT NULL
        )",
        [],
    ).expect("Failed to create table");

    let state = web::Data::new(AppState {
        db: Mutex::new(conn),
    });

    HttpServer::new(move || {
        App::new()
            .app_data(state.clone())
            .route("/recommender", web::get().to(get_recommender))
            .route("/recommender", web::post().to(post_recommender))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}

async fn get_recommender(state: web::Data<AppState>, query: web::Query<HashMap<String, String>>) -> impl Responder {
    let tags = match query.get("tags") {
        Some(tags) => tags.split(',').collect::<Vec<&str>>(),
        None => return HttpResponse::BadRequest().body("Missing 'tags' parameter"),
    };

    let db = state.db.lock().unwrap();
    let mut stmt = db.prepare("SELECT product_name, tags FROM products WHERE tags LIKE ?")?;
    let mut results = Vec::new();

    for tag in tags {
        let tag_query = format!("%{}%", tag);
        let rows = stmt.query_map(params![tag_query], |row| {
            Ok(Product {
                product_name: row.get(0)?,
                tags: row.get::<_, String>(1)?.split(',').map(String::from).collect(),
            })
        })?;

        for product in rows {
            if let Ok(product) = product {
                results.push(product);
            }
        }
    }

    let html_response = results.iter()
        .map(|p| format!("<div><h2>{}</h2><p>Tags: {}</p></div>", p.product_name, p.tags.join(", ")))
        .collect::<String>();

    HttpResponse::Ok().content_type("text/html").body(html_response)
}

async fn post_recommender(state: web::Data<AppState>, product: web::Json<Product>) -> impl Responder {
    let db = state.db.lock().unwrap();
    let tags = product.tags.join(",");
    
    if product.product_name.is_empty() || product.tags.is_empty() {
        return HttpResponse::BadRequest().body("Invalid input");
    }

    match db.execute("INSERT INTO products (product_name, tags) VALUES (?, ?)", params![product.product_name, tags]) {
        Ok(_) => {
            info!("Product added: {:?}", product);
            HttpResponse::Ok().body("Product added successfully")
        },
        Err(err) => {
            error!("Failed to add product: {}", err);
            HttpResponse::InternalServerError().body("Failed to add product")
        }
    }
}