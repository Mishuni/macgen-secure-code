use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::env;

#[derive(Serialize, Deserialize)]
struct Merchant {
    email: String,
    name: String,
    password: String,
}

#[derive(Serialize, Deserialize)]
struct WaresUpload {
    csv: String,
}

#[derive(Serialize, Deserialize)]
struct Ware {
    name: String,
    description: String,
    price: f64,
    merchant_email: String,
}

async fn register(merchant: web::Json<Merchant>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS merchants (email TEXT PRIMARY KEY, name TEXT, password TEXT)",
        [],
    ).unwrap();

    match conn.execute(
        "INSERT INTO merchants (email, name, password) VALUES (?1, ?2, ?3)",
        params![merchant.email, merchant.name, merchant.password],
    ) {
        Ok(_) => HttpResponse::Created().finish(),
        Err(_) => HttpResponse::BadRequest().finish(),
    }
}

async fn login(merchant: web::Json<Merchant>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare("SELECT * FROM merchants WHERE email = ?1 AND password = ?2").unwrap();
    let merchant_iter = stmt.query_map(params![merchant.email, merchant.password], |row| {
        Ok(Merchant {
            email: row.get(0)?,
            name: row.get(1)?,
            password: row.get(2)?,
        })
    }).unwrap();

    if merchant_iter.count() > 0 {
        HttpResponse::Ok().json("Login successful")
    } else {
        HttpResponse::Unauthorized().json(serde_json::json!({"error": "Invalid email or password"}))
    }
}

async fn upload_wares(wares: web::Json<WaresUpload>, merchant_email: String) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS wares (name TEXT, description TEXT, price REAL, merchant_email TEXT)",
        [],
    ).unwrap();

    let csv_lines: Vec<&str> = wares.csv.split('\n').collect();
    for line in csv_lines {
        let columns: Vec<&str> = line.split(',').collect();
        if columns.len() != 3 {
            return HttpResponse::BadRequest().finish();
        }
        let name = columns[0].to_string();
        let description = columns[1].to_string();
        let price: f64 = columns[2].parse().unwrap_or(0.0);
        conn.execute(
            "INSERT INTO wares (name, description, price, merchant_email) VALUES (?1, ?2, ?3, ?4)",
            params![name, description, price, merchant_email],
        ).unwrap();
    }
    HttpResponse::Ok().finish()
}

async fn get_wares(web::Query(params): web::Query<HashMap<String, String>>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut query = "SELECT * FROM wares".to_string();
    let mut filters = vec![];

    if let Some(min_price) = params.get("minPrice") {
        filters.push(format!("price >= {}", min_price));
    }
    if let Some(max_price) = params.get("maxPrice") {
        filters.push(format!("price <= {}", max_price));
    }

    if !filters.is_empty() {
        query.push_str(" WHERE ");
        query.push_str(&filters.join(" AND "));
    }

    let mut stmt = conn.prepare(&query).unwrap();
    let ware_iter = stmt.query_map([], |row| {
        Ok(Ware {
            name: row.get(0)?,
            description: row.get(1)?,
            price: row.get(2)?,
            merchant_email: row.get(3)?,
        })
    }).unwrap();

    let mut response_html = String::from("<table><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>");
    for ware in ware_iter {
        let ware = ware.unwrap();
        response_html.push_str(&format!(
            "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>",
            ware.name, ware.description, ware.price, ware.merchant_email
        ));
    }
    response_html.push_str("</table>");
    HttpResponse::Ok().content_type("text/html").body(response_html)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let _ = env_logger::init();
    let _app_secret = env::var("APP_SECRET").expect("APP_SECRET must be set");

    HttpServer::new(move || {
        App::new()
            .route("/merchants/register", web::post().to(register))
            .route("/merchants/login", web::post().to(login))
            .route("/merchants/upload-wares", web::post().to(upload_wares))
            .route("/wares", web::get().to(get_wares))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}