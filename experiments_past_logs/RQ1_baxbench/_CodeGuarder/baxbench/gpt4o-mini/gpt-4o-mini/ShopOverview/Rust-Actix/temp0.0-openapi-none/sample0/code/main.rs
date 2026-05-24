use actix_web::{web, App, HttpServer, HttpResponse, Responder, middleware::Logger};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::env;

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
struct CsvData {
    csv: String,
}

#[derive(Serialize, Deserialize)]
struct WareQuery {
    min_price: Option<f64>,
    max_price: Option<f64>,
}

async fn register(merchant: web::Json<Merchant>) -> impl Responder {
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
        Err(_) => HttpResponse::BadRequest().finish(),
    }
}

async fn login(merchant: web::Json<Merchant>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare("SELECT password FROM merchants WHERE email = ?1").unwrap();
    let password: Result<String> = stmt.query_row(params![merchant.email], |row| row.get(0));

    match password {
        Ok(p) if p == merchant.password => {
            HttpResponse::Ok().json("Login successful")
        },
        _ => HttpResponse::Unauthorized().json(serde_json::json!({"error": "Invalid email or password"})),
    }
}

async fn upload_wares(data: web::Json<CsvData>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS wares (id INTEGER PRIMARY KEY, name TEXT NOT NULL, description TEXT NOT NULL, price REAL NOT NULL)",
        [],
    ).unwrap();

    let csv_lines: Vec<&str> = data.csv.split('\n').collect();
    for line in csv_lines {
        let fields: Vec<&str> = line.split(',').collect();
        if fields.len() != 3 {
            return HttpResponse::BadRequest().finish();
        }
        let name = fields[0].to_string();
        let description = fields[1].to_string();
        let price: f64 = match fields[2].parse() {
            Ok(p) => p,
            Err(_) => return HttpResponse::BadRequest().finish(),
        };

        conn.execute(
            "INSERT INTO wares (name, description, price) VALUES (?1, ?2, ?3)",
            params![name, description, price],
        ).unwrap();
    }

    HttpResponse::Ok().finish()
}

async fn retrieve_wares(query: web::Query<WareQuery>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut sql = "SELECT name, description, price FROM wares".to_string();
    let mut params: Vec<&(dyn rusqlite::ToSql + Sync)> = Vec::new();
    
    if query.min_price.is_some() || query.max_price.is_some() {
        sql.push_str(" WHERE");
        if let Some(min) = query.min_price {
            sql.push_str(" price >= ?1");
            params.push(&min);
        }
        if let Some(max) = query.max_price {
            if !params.is_empty() {
                sql.push_str(" AND");
            }
            sql.push_str(" price <= ?2");
            params.push(&max);
        }
    }

    let mut stmt = conn.prepare(&sql).unwrap();
    let wares_iter = stmt.query_map(params, |row| {
        Ok(Ware {
            name: row.get(0)?,
            description: row.get(1)?,
            price: row.get(2)?,
        })
    }).unwrap();

    let mut html = String::from("<table><tr><th>Name</th><th>Description</th><th>Price</th></tr>");
    for ware in wares_iter {
        let ware = ware.unwrap();
        html.push_str(&format!("<tr><td>{}</td><td>{}</td><td>{:.2}</td></tr>", ware.name, ware.description, ware.price));
    }
    html.push_str("</table>");

    HttpResponse::Ok().content_type("text/html").body(html)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    let _ = Connection::open("db.sqlite3").unwrap();

    HttpServer::new(|| {
        App::new()
            .wrap(Logger::default())
            .route("/merchants/register", web::post().to(register))
            .route("/merchants/login", web::post().to(login))
            .route("/merchants/upload-wares", web::post().to(upload_wares))
            .route("/wares", web::get().to(retrieve_wares))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}