use actix_web::{web, App, HttpServer, HttpResponse, Responder, post, get, HttpRequest};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
use std::env;

#[derive(Deserialize)]
struct RegisterMerchant {
    email: String,
    name: String,
    password: String,
}

#[derive(Deserialize)]
struct LoginMerchant {
    email: String,
    password: String,
}

#[derive(Deserialize)]
struct UploadWares {
    csv: String,
}

#[derive(Serialize)]
struct Ware {
    name: String,
    description: String,
    price: f64,
    merchant_email: String,
}

async fn register_merchant(data: web::Json<RegisterMerchant>) -> impl Responder {
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
        Err(_) => HttpResponse::BadRequest().finish(),
    }
}

async fn login_merchant(data: web::Json<LoginMerchant>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare("SELECT password FROM merchants WHERE email = ?1").unwrap();
    let mut rows = stmt.query(params![data.email]).unwrap();

    if let Some(row) = rows.next().unwrap() {
        let stored_password: String = row.get(0).unwrap();
        if stored_password == data.password {
            return HttpResponse::Ok().json("Login successful");
        }
    }
    HttpResponse::Unauthorized().json(serde_json::json!({"error": "Invalid email or password"}))
}

async fn upload_wares(req: HttpRequest, data: web::Json<UploadWares>) -> impl Responder {
    if req.cookie("AUTH_COOKIE").is_none() {
        return HttpResponse::Unauthorized().finish();
    }

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

    let csv_data = &data.csv;
    let lines: Vec<&str> = csv_data.split('\n').collect();
    for line in lines {
        let columns: Vec<&str> = line.split(',').collect();
        if columns.len() != 3 {
            return HttpResponse::BadRequest().finish();
        }
        let name = columns[0].trim();
        let description = columns[1].trim();
        let price: f64 = columns[2].trim().parse().unwrap_or(0.0);

        conn.execute(
            "INSERT INTO wares (name, description, price, merchant_email) VALUES (?1, ?2, ?3, ?4)",
            params![name, description, price, "merchant@example.com"],
        ).unwrap();
    }
    HttpResponse::Ok().finish()
}

async fn get_wares(req: HttpRequest, web::Query(info): web::Query<std::collections::HashMap<String, String>>) -> impl Responder {
    if req.cookie("AUTH_COOKIE").is_none() {
        return HttpResponse::Unauthorized().finish();
    }

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

    let mut html = String::from("<table><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>");
    for ware in ware_iter {
        let ware = ware.unwrap();
        html.push_str(&format!(
            "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>",
            ware.name, ware.description, ware.price, ware.merchant_email
        ));
    }
    html.push_str("</table>");
    HttpResponse::Ok().content_type("text/html").body(html)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    HttpServer::new(|| {
        App::new()
            .service(web::resource("/merchants/register").route(post().to(register_merchant)))
            .service(web::resource("/merchants/login").route(post().to(login_merchant)))
            .service(web::resource("/merchants/upload-wares").route(post().to(upload_wares)))
            .service(web::resource("/wares").route(get().to(get_wares)))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}