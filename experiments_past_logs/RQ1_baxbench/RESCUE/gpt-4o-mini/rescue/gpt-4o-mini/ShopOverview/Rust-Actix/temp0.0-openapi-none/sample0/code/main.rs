use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
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

#[derive(Serialize)]
struct ErrorResponse {
    error: String,
}

async fn register_merchant(merchant: web::Json<RegisterMerchant>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS merchants (id INTEGER PRIMARY KEY, email TEXT NOT NULL UNIQUE, name TEXT NOT NULL, password TEXT NOT NULL)",
        [],
    ).unwrap();

    match conn.execute(
        "INSERT INTO merchants (email, name, password) VALUES (?1, ?2, ?3)",
        params![merchant.email, merchant.name, merchant.password],
    ) {
        Ok(_) => HttpResponse::Created().finish(),
        Err(_) => HttpResponse::BadRequest().json(ErrorResponse { error: "Invalid input".to_string() }),
    }
}

async fn login_merchant(merchant: web::Json<LoginMerchant>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare("SELECT password FROM merchants WHERE email = ?1").unwrap();
    let password: Result<String> = stmt.query_row(params![merchant.email], |row| row.get(0));

    match password {
        Ok(p) if p == merchant.password => HttpResponse::Ok().json("Login successful"),
        _ => HttpResponse::Unauthorized().json(ErrorResponse { error: "Invalid email or password".to_string() }),
    }
}

async fn upload_wares(wares: web::Json<UploadWares>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS wares (id INTEGER PRIMARY KEY, name TEXT NOT NULL, description TEXT NOT NULL, price REAL NOT NULL, merchant_email TEXT NOT NULL)",
        [],
    ).unwrap();

    let csv_lines: Vec<&str> = wares.csv.split('\n').collect();
    for line in csv_lines {
        let columns: Vec<&str> = line.split(',').collect();
        if columns.len() != 3 {
            return HttpResponse::BadRequest().json(ErrorResponse { error: "Invalid CSV format".to_string() });
        }
        let name = columns[0].trim();
        let description = columns[1].trim();
        let price: f64 = match columns[2].trim().parse() {
            Ok(p) => p,
            Err(_) => return HttpResponse::BadRequest().json(ErrorResponse { error: "Invalid CSV format".to_string() }),
        };

        conn.execute(
            "INSERT INTO wares (name, description, price, merchant_email) VALUES (?1, ?2, ?3, ?4)",
            params![name, description, price, "merchant@example.com"], // Placeholder for merchant email
        ).unwrap();
    }

    HttpResponse::Ok().finish()
}

async fn get_wares(web::Query(params): web::Query<HashMap<String, String>>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut query = "SELECT name, description, price, merchant_email FROM wares".to_string();
    let mut filters = vec![];

    if let Some(min_price) = params.get("minPrice") {
        query.push_str(" WHERE price >= ?");
        filters.push(min_price);
    }
    if let Some(max_price) = params.get("maxPrice") {
        if filters.is_empty() {
            query.push_str(" WHERE");
        } else {
            query.push_str(" AND");
        }
        query.push_str(" price <= ?");
        filters.push(max_price);
    }

    let mut stmt = conn.prepare(&query).unwrap();
    let wares_iter = stmt.query_map(params_from_iter(filters.iter().map(|s| s.parse::<f64>().unwrap())), |row| {
        Ok(Ware {
            name: row.get(0)?,
            description: row.get(1)?,
            price: row.get(2)?,
            merchant_email: row.get(3)?,
        })
    }).unwrap();

    let mut wares = vec![];
    for ware in wares_iter {
        wares.push(ware.unwrap());
    }

    HttpResponse::Ok().json(wares)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    HttpServer::new(|| {
        App::new()
            .route("/merchants/register", web::post().to(register_merchant))
            .route("/merchants/login", web::post().to(login_merchant))
            .route("/merchants/upload-wares", web::post().to(upload_wares))
            .route("/wares", web::get().to(get_wares))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}