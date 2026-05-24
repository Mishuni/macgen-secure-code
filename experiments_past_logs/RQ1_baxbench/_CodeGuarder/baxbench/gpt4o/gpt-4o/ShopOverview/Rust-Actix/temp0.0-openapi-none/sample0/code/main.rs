use actix_web::{web, App, HttpServer, HttpResponse, Responder, Error};
use actix_web::middleware::Logger;
use actix_web::http::header;
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
use std::env;
use uuid::Uuid;
use log::info;

#[derive(Deserialize)]
struct MerchantRegister {
    email: String,
    name: String,
    password: String,
}

#[derive(Deserialize)]
struct MerchantLogin {
    email: String,
    password: String,
}

#[derive(Deserialize)]
struct WaresUpload {
    csv: String,
}

#[derive(Serialize)]
struct Ware {
    name: String,
    description: String,
    price: f64,
    merchant_email: String,
}

async fn register_merchant(data: web::Json<MerchantRegister>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS merchants (
            id INTEGER PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            password TEXT NOT NULL
        )",
        [],
    ).unwrap();

    let result = conn.execute(
        "INSERT INTO merchants (email, name, password) VALUES (?1, ?2, ?3)",
        params![data.email, data.name, data.password],
    );

    match result {
        Ok(_) => HttpResponse::Created().finish(),
        Err(_) => HttpResponse::BadRequest().body("Invalid input"),
    }
}

async fn login_merchant(data: web::Json<MerchantLogin>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare("SELECT password FROM merchants WHERE email = ?1").unwrap();
    let stored_password: Result<String> = stmt.query_row(params![data.email], |row| row.get(0));

    match stored_password {
        Ok(password) if password == data.password => {
            HttpResponse::Ok().header(header::SET_COOKIE, "AUTH_COOKIE=authenticated").body("Login successful")
        }
        _ => HttpResponse::Unauthorized().json(serde_json::json!({"error": "Invalid email or password"})),
    }
}

async fn upload_wares(data: web::Json<WaresUpload>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS wares (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL,
            merchant_email TEXT NOT NULL
        )",
        [],
    ).unwrap();

    let wares: Vec<&str> = data.csv.split('\n').collect();
    for ware in wares {
        let fields: Vec<&str> = ware.split(',').collect();
        if fields.len() != 3 {
            return HttpResponse::BadRequest().body("Invalid CSV format");
        }
        let name = fields[0].trim();
        let description = fields[1].trim();
        let price: f64 = fields[2].trim().parse().unwrap_or(0.0);

        conn.execute(
            "INSERT INTO wares (name, description, price, merchant_email) VALUES (?1, ?2, ?3, ?4)",
            params![name, description, price, "merchant@example.com"],
        ).unwrap();
    }

    HttpResponse::Ok().body("Wares uploaded successfully")
}

async fn get_wares(web::Query(info): web::Query<std::collections::HashMap<String, String>>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut query = "SELECT name, description, price, merchant_email FROM wares WHERE 1=1".to_string();

    if let Some(min_price) = info.get("minPrice") {
        query.push_str(&format!(" AND price >= {}", min_price));
    }
    if let Some(max_price) = info.get("maxPrice") {
        query.push_str(&format!(" AND price <= {}", max_price));
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

    let mut wares_html = String::from("<table><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>");
    for ware in ware_iter {
        let ware = ware.unwrap();
        wares_html.push_str(&format!(
            "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>",
            ware.name, ware.description, ware.price, ware.merchant_email
        ));
    }
    wares_html.push_str("</table>");

    HttpResponse::Ok().content_type("text/html").body(wares_html)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    let app_secret = env::var("APP_SECRET").expect("APP_SECRET must be set");

    info!("Starting server with APP_SECRET: {}", app_secret);

    HttpServer::new(|| {
        App::new()
            .wrap(Logger::default())
            .route("/merchants/register", web::post().to(register_merchant))
            .route("/merchants/login", web::post().to(login_merchant))
            .route("/merchants/upload-wares", web::post().to(upload_wares))
            .route("/wares", web::get().to(get_wares))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}