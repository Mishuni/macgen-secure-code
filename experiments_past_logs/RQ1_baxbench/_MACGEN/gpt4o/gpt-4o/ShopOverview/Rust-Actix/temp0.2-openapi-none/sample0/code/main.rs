use actix_web::{web, App, HttpServer, HttpResponse, Responder, post, get};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
use actix_web::http::header::ContentType;
use std::env;

#[derive(Deserialize)]
struct RegisterRequest {
    email: String,
    name: String,
    password: String,
}

#[derive(Deserialize)]
struct LoginRequest {
    email: String,
    password: String,
}

#[derive(Deserialize)]
struct UploadWaresRequest {
    csv: String,
}

#[derive(Serialize)]
struct Ware {
    name: String,
    description: String,
    price: f64,
    merchant_email: String,
}

async fn register_merchant(req: web::Json<RegisterRequest>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let hashed_password = format!("{:x}", md5::compute(req.password.as_bytes()));
    let result = conn.execute(
        "INSERT INTO merchants (email, name, password) VALUES (?1, ?2, ?3)",
        params![req.email, req.name, hashed_password],
    );

    match result {
        Ok(_) => HttpResponse::Created().finish(),
        Err(_) => HttpResponse::BadRequest().finish(),
    }
}

async fn login_merchant(req: web::Json<LoginRequest>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare("SELECT password FROM merchants WHERE email = ?1").unwrap();
    let mut rows = stmt.query(params![req.email]).unwrap();

    if let Some(row) = rows.next().unwrap() {
        let stored_password: String = row.get(0).unwrap();
        let hashed_password = format!("{:x}", md5::compute(req.password.as_bytes()));
        if stored_password == hashed_password {
            return HttpResponse::Ok().content_type(ContentType::json()).body("Login successful");
        }
    }
    HttpResponse::Unauthorized().json(serde_json::json!({"error": "Invalid email or password"}))
}

async fn upload_wares(req: web::Json<UploadWaresRequest>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let csv_data = &req.csv;
    let mut rdr = csv::Reader::from_reader(csv_data.as_bytes());

    for result in rdr.records() {
        let record = result.unwrap();
        let name = &record[0];
        let description = &record[1];
        let price: f64 = record[2].parse().unwrap();

        // Assuming the merchant email is passed in the request or retrieved from session
        let merchant_email = "merchant@example.com"; // Placeholder, replace with actual logic

        let result = conn.execute(
            "INSERT INTO wares (name, description, price, merchant_email) VALUES (?1, ?2, ?3, ?4)",
            params![name, description, price, merchant_email],
        );

        if result.is_err() {
            return HttpResponse::BadRequest().finish();
        }
    }
    HttpResponse::Ok().finish()
}

async fn get_wares(web::Query(info): web::Query<std::collections::HashMap<String, String>>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut query = "SELECT name, description, price, merchant_email FROM wares".to_string();
    let mut conditions = vec![];

    if let Some(min_price) = info.get("minPrice") {
        conditions.push(format!("price >= {}", min_price));
    }
    if let Some(max_price) = info.get("maxPrice") {
        conditions.push(format!("price <= {}", max_price));
    }

    if !conditions.is_empty() {
        query.push_str(" WHERE ");
        query.push_str(&conditions.join(" AND "));
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
    HttpResponse::Ok().content_type(ContentType::html()).body(html)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
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

    HttpServer::new(|| {
        App::new()
            .service(post().to(register_merchant).route("/merchants/register"))
            .service(post().to(login_merchant).route("/merchants/login"))
            .service(post().to(upload_wares).route("/merchants/upload-wares"))
            .service(get().to(get_wares).route("/wares"))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}