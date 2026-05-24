use actix_web::{web, App, HttpResponse, HttpServer, Responder, post, get, middleware};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::env;
use regex::Regex;
use md5;

#[derive(Serialize, Deserialize)]
struct Merchant {
    email: String,
    name: String,
    password: String,
}

#[derive(Serialize, Deserialize)]
struct Ware {
    name: String,
    description: String,
    price: f64,
}

#[derive(Serialize, Deserialize)]
struct CsvInput {
    csv: String,
}

#[derive(Serialize, Deserialize)]
struct WaresResponse {
    wares: Vec<Ware>,
}

#[post("/merchants/register")]
async fn register(merchant: web::Json<Merchant>) -> impl Responder {
    let email_regex = Regex::new(r"^[\w\.-]+@[\w\.-]+\.\w+$").unwrap();
    if !email_regex.is_match(&merchant.email) || merchant.name.is_empty() || merchant.password.is_empty() {
        return HttpResponse::BadRequest().finish();
    }

    let password_hash = format!("{:x}", md5::compute(&merchant.password));

    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS merchants (email TEXT PRIMARY KEY, name TEXT, password TEXT)",
        [],
    ).unwrap();

    match conn.execute(
        "INSERT INTO merchants (email, name, password) VALUES (?1, ?2, ?3)",
        params![merchant.email, merchant.name, password_hash],
    ) {
        Ok(_) => HttpResponse::Created().finish(),
        Err(_) => HttpResponse::BadRequest().finish(),
    }
}

#[post("/merchants/login")]
async fn login(merchant: web::Json<Merchant>) -> impl Responder {
    let email_regex = Regex::new(r"^[\w\.-]+@[\w\.-]+\.\w+$").unwrap();
    if !email_regex.is_match(&merchant.email) || merchant.password.is_empty() {
        return HttpResponse::BadRequest().finish();
    }

    let password_hash = format!("{:x}", md5::compute(&merchant.password));

    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare("SELECT email FROM merchants WHERE email = ?1 AND password = ?2").unwrap();
    let mut rows = stmt.query(params![merchant.email, password_hash]).unwrap();

    if rows.next().is_ok() {
        HttpResponse::Ok().json("Login successful")
    } else {
        HttpResponse::Unauthorized().json(serde_json::json!({"error": "Invalid email or password"}))
    }
}

#[post("/merchants/upload-wares")]
async fn upload_wares(input: web::Json<CsvInput>) -> impl Responder {
    if input.csv.is_empty() {
        return HttpResponse::BadRequest().finish();
    }

    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS wares (name TEXT, description TEXT, price REAL)",
        [],
    ).unwrap();

    let csv_lines: Vec<&str> = input.csv.lines().collect();
    for line in csv_lines {
        let parts: Vec<&str> = line.split(',').collect();
        if parts.len() != 3 || parts.iter().any(|&s| s.is_empty()) {
            return HttpResponse::BadRequest().finish();
        }
        let name = parts[0].to_string();
        let description = parts[1].to_string();
        let price: f64 = parts[2].parse().unwrap_or(0.0);

        conn.execute(
            "INSERT INTO wares (name, description, price) VALUES (?1, ?2, ?3)",
            params![name, description, price],
        ).unwrap();
    }

    HttpResponse::Ok().finish()
}

#[get("/wares")]
async fn get_wares(web::Query(params): web::Query<std::collections::HashMap<String, String>>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut query = "SELECT name, description, price FROM wares".to_string();
    let mut filters = Vec::new();

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
    let wares_iter = stmt.query_map(params_from_iter(filters.iter()), |row| {
        Ok(Ware {
            name: row.get(0)?,
            description: row.get(1)?,
            price: row.get(2)?,
        })
    }).unwrap();

    let wares: Vec<Ware> = wares_iter.filter_map(Result::ok).collect();
    HttpResponse::Ok().json(WaresResponse { wares })
}

fn params_from_iter<'a, I>(iter: I) -> Vec<&'a (dyn rusqlite::ToSql + 'a)>
where
    I: Iterator<Item = &'a String>,
{
    iter.map(|s| s as &(dyn rusqlite::ToSql + 'a)).collect()
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let _ = env_logger::init();
    let app_secret = env::var("APP_SECRET").expect("APP_SECRET must be set");

    HttpServer::new(move || {
        App::new()
            .wrap(middleware::Logger::default())
            .service(register)
            .service(login)
            .service(upload_wares)
            .service(get_wares)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}