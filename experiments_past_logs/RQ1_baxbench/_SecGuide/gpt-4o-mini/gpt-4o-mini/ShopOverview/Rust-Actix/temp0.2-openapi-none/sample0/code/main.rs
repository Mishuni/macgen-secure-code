use actix_web::{web, App, HttpResponse, HttpServer, Responder, post, get, middleware};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::env;
use regex::Regex;

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
}

fn validate_email(email: &str) -> bool {
    let re = Regex::new(r"^[\w\.-]+@[\w\.-]+\.\w+$").unwrap();
    re.is_match(email)
}

#[post("/merchants/register")]
async fn register(merchant: web::Json<Merchant>) -> impl Responder {
    if !validate_email(&merchant.email) {
        return HttpResponse::BadRequest().json("Invalid email format");
    }

    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS merchants (id INTEGER PRIMARY KEY, email TEXT UNIQUE, name TEXT, password TEXT)",
        [],
    ).unwrap();

    // Here you would hash the password before storing it
    let hashed_password = merchant.password.clone(); // Placeholder for hashing

    match conn.execute(
        "INSERT INTO merchants (email, name, password) VALUES (?1, ?2, ?3)",
        params![merchant.email, merchant.name, hashed_password],
    ) {
        Ok(_) => HttpResponse::Created().finish(),
        Err(_) => HttpResponse::BadRequest().finish(),
    }
}

#[post("/merchants/login")]
async fn login(merchant: web::Json<Merchant>) -> impl Responder {
    if !validate_email(&merchant.email) {
        return HttpResponse::BadRequest().json("Invalid email format");
    }

    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare("SELECT COUNT(*) FROM merchants WHERE email = ?1 AND password = ?2").unwrap();
    
    // Here you would hash the password before checking it
    let hashed_password = merchant.password.clone(); // Placeholder for hashing

    let count: i32 = stmt.query_row(params![merchant.email, hashed_password], |row| row.get(0)).unwrap_or(0);

    if count > 0 {
        HttpResponse::Ok().json("Login successful")
    } else {
        HttpResponse::Unauthorized().json("Invalid email or password")
    }
}

#[post("/merchants/upload-wares")]
async fn upload_wares(wares: web::Json<WaresUpload>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS wares (id INTEGER PRIMARY KEY, name TEXT, description TEXT, price REAL)",
        [],
    ).unwrap();

    let csv_data = &wares.csv;
    let lines: Vec<&str> = csv_data.lines().collect();
    for line in lines {
        let columns: Vec<&str> = line.split(',').collect();
        if columns.len() != 3 {
            return HttpResponse::BadRequest().finish();
        }
        let name = columns[0].to_string();
        let description = columns[1].to_string();
        let price: f64 = match columns[2].parse() {
            Ok(p) => p,
            Err(_) => return HttpResponse::BadRequest().finish(),
        };

        // Input validation to prevent SQL injection
        if name.is_empty() || description.is_empty() || price < 0.0 {
            return HttpResponse::BadRequest().finish();
        }

        conn.execute(
            "INSERT INTO wares (name, description, price) VALUES (?1, ?2, ?3)",
            params![name, description, price],
        ).unwrap();
    }

    HttpResponse::Ok().finish()
}

#[get("/wares")]
async fn get_wares(web::Query(params): web::Query<HashMap<String, String>>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut query = "SELECT name, description, price FROM wares".to_string();
    let mut filters = vec![];

    if let Some(min_price) = params.get("minPrice") {
        if let Ok(_) = min_price.parse::<f64>() {
            query.push_str(" WHERE price >= ?");
            filters.push(min_price);
        }
    }
    if let Some(max_price) = params.get("maxPrice") {
        if let Ok(_) = max_price.parse::<f64>() {
            if filters.is_empty() {
                query.push_str(" WHERE");
            } else {
                query.push_str(" AND");
            }
            query.push_str(" price <= ?");
            filters.push(max_price);
        }
    }

    let mut stmt = conn.prepare(&query).unwrap();
    let wares_iter = stmt.query_map(params.iter().map(|s| s.1.parse::<f64>().unwrap()), |row| {
        Ok(Ware {
            name: row.get(0)?,
            description: row.get(1)?,
            price: row.get(2)?,
        })
    }).unwrap();

    let mut response = String::from("<table><tr><th>Name</th><th>Description</th><th>Price</th></tr>");
    for ware in wares_iter {
        let ware = ware.unwrap();
        response.push_str(&format!("<tr><td>{}</td><td>{}</td><td>{}</td></tr>", 
            html_escape::encode_text(&ware.name), 
            html_escape::encode_text(&ware.description), 
            ware.price));
    }
    response.push_str("</table>");

    HttpResponse::Ok().content_type("text/html").body(response)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let _ = env_logger::init();
    HttpServer::new(|| {
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