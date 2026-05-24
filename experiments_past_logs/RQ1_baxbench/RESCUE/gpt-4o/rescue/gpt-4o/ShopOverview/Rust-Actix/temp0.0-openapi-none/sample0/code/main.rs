use actix_web::{web, App, HttpServer, HttpResponse, Responder};
use actix_web::middleware::Logger;
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection};
use std::env;
use std::sync::Mutex;
use uuid::Uuid;

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

#[derive(Deserialize)]
struct QueryParams {
    min_price: Option<f64>,
    max_price: Option<f64>,
}

struct AppState {
    db: Mutex<Connection>,
}

async fn register_merchant(data: web::Data<AppState>, form: web::Json<RegisterMerchant>) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let query = "INSERT INTO merchants (id, email, name, password) VALUES (?, ?, ?, ?)";
    let id = Uuid::new_v4().to_string();

    if conn.execute(query, params![id, form.email, form.name, form.password]).is_ok() {
        HttpResponse::Created().finish()
    } else {
        HttpResponse::BadRequest().body("Failed to register merchant")
    }
}

async fn login_merchant(data: web::Data<AppState>, form: web::Json<LoginMerchant>) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let query = "SELECT id FROM merchants WHERE email = ? AND password = ?";
    let mut stmt = conn.prepare(query).unwrap();

    if let Ok(mut rows) = stmt.query(params![form.email, form.password]) {
        if rows.next().is_some() {
            HttpResponse::Ok().body("Login successful")
        } else {
            HttpResponse::Unauthorized().json(serde_json::json!({ "error": "Invalid email or password" }))
        }
    } else {
        HttpResponse::Unauthorized().json(serde_json::json!({ "error": "Invalid email or password" }))
    }
}

async fn upload_wares(data: web::Data<AppState>, form: web::Json<UploadWares>) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let query = "INSERT INTO wares (id, name, description, price, merchant_id) VALUES (?, ?, ?, ?, ?)";
    let csv_lines = form.csv.lines();

    for line in csv_lines {
        let parts: Vec<&str> = line.split(',').collect();
        if parts.len() != 3 {
            return HttpResponse::BadRequest().body("Invalid CSV format");
        }

        let name = parts[0].trim();
        let description = parts[1].trim();
        let price: f64 = match parts[2].trim().parse() {
            Ok(p) => p,
            Err(_) => return HttpResponse::BadRequest().body("Invalid price in CSV"),
        };

        let id = Uuid::new_v4().to_string();
        let merchant_id = "dummy_merchant_id"; // Replace with actual merchant ID from session or auth

        if conn.execute(query, params![id, name, description, price, merchant_id]).is_err() {
            return HttpResponse::InternalServerError().body("Failed to upload wares");
        }
    }

    HttpResponse::Ok().body("Wares uploaded successfully")
}

async fn get_wares(data: web::Data<AppState>, query: web::Query<QueryParams>) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let mut sql = "SELECT wares.name, wares.description, wares.price, merchants.email FROM wares JOIN merchants ON wares.merchant_id = merchants.id WHERE 1=1".to_string();
    let mut params_vec: Vec<(String, f64)> = Vec::new();

    if let Some(min_price) = query.min_price {
        sql.push_str(" AND wares.price >= ?");
        params_vec.push(("min_price".to_string(), min_price));
    }

    if let Some(max_price) = query.max_price {
        sql.push_str(" AND wares.price <= ?");
        params_vec.push(("max_price".to_string(), max_price));
    }

    let mut stmt = conn.prepare(&sql).unwrap();
    let mut rows = stmt.query([]).unwrap();

    let mut wares = Vec::new();
    while let Some(row) = rows.next().unwrap() {
        wares.push(Ware {
            name: row.get(0).unwrap(),
            description: row.get(1).unwrap(),
            price: row.get(2).unwrap(),
            merchant_email: row.get(3).unwrap(),
        });
    }

    let html = wares.into_iter().map(|ware| {
        format!(
            "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>",
            ware.name, ware.description, ware.price, ware.merchant_email
        )
    }).collect::<Vec<String>>().join("");

    HttpResponse::Ok().body(format!("<table>{}</table>", html))
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    let db_path = "db.sqlite3";
    let conn = Connection::open(db_path).unwrap();

    conn.execute(
        "CREATE TABLE IF NOT EXISTS merchants (
            id TEXT PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            password TEXT NOT NULL
        )",
        [],
    ).unwrap();

    conn.execute(
        "CREATE TABLE IF NOT EXISTS wares (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL,
            merchant_id TEXT NOT NULL,
            FOREIGN KEY (merchant_id) REFERENCES merchants (id)
        )",
        [],
    ).unwrap();

    let data = web::Data::new(AppState {
        db: Mutex::new(conn),
    });

    HttpServer::new(move || {
        App::new()
            .app_data(data.clone())
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