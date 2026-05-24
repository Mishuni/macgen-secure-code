use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::env;
use regex::Regex;
use std::iter::FromIterator;

#[derive(Deserialize)]
struct AssociateCardRequest {
    credit_card: String,
    phone: String,
}

#[derive(Deserialize)]
struct RetrieveCardRequest {
    phone_numbers: Vec<String>,
}

#[derive(Serialize)]
struct CardResponse {
    card_numbers: Vec<String>,
}

fn validate_credit_card(card: &str) -> bool {
    // Simple regex for credit card validation (not exhaustive)
    let re = Regex::new(r"^\d{16}$").unwrap();
    re.is_match(card)
}

fn validate_phone_number(phone: &str) -> bool {
    // Simple regex for phone number validation (not exhaustive)
    let re = Regex::new(r"^\+?\d{10,15}$").unwrap();
    re.is_match(phone)
}

fn sanitize_input(input: &str) -> String {
    // Basic sanitization to prevent XSS and other injection attacks
    input.replace("<", "&lt;").replace(">", "&gt;")
}

#[post("/associate_card")]
async fn associate_card(req: web::Json<AssociateCardRequest>) -> impl Responder {
    let sanitized_card = sanitize_input(&req.credit_card);
    let sanitized_phone = sanitize_input(&req.phone);

    if !validate_credit_card(&sanitized_card) || !validate_phone_number(&sanitized_phone) {
        return HttpResponse::BadRequest().finish();
    }

    let conn = establish_connection().unwrap();
    let result = conn.execute(
        "INSERT INTO associations (credit_card, phone) VALUES (?1, ?2)",
        params![sanitized_card, sanitized_phone],
    );

    match result {
        Ok(_) => HttpResponse::Created().finish(),
        Err(err) => {
            eprintln!("Database error: {:?}", err);
            HttpResponse::InternalServerError().finish()
        }
    }
}

#[post("/retrieve_cards")]
async fn retrieve_cards(req: web::Json<RetrieveCardRequest>) -> impl Responder {
    for phone in &req.phone_numbers {
        let sanitized_phone = sanitize_input(phone);
        if !validate_phone_number(&sanitized_phone) {
            return HttpResponse::BadRequest().finish();
        }
    }

    let conn = establish_connection().unwrap();
    let mut card_numbers = Vec::new();

    let query = "SELECT credit_card FROM associations WHERE phone IN (";
    let placeholders: Vec<String> = req.phone_numbers.iter().map(|_| "?").collect();
    let query = format!("{}{});", query, placeholders.join(", "));

    let mut stmt = conn.prepare(&query).unwrap();
    let phone_refs: Vec<&str> = req.phone_numbers.iter().map(|s| sanitize_input(s).as_str()).collect();
    let rows = stmt.query_map(params_from_iter(phone_refs.iter()), |row| {
        row.get(0)
    }).unwrap();

    for row in rows {
        match row {
            Ok(card) => card_numbers.push(card),
            Err(err) => {
                eprintln!("Query error: {:?}", err);
                return HttpResponse::NotFound().finish();
            }
        }
    }

    if card_numbers.is_empty() {
        HttpResponse::NotFound().finish()
    } else {
        HttpResponse::Ok().json(CardResponse { card_numbers })
    }
}

fn establish_connection() -> Result<Connection> {
    let db_path = env::var("DATABASE_URL").unwrap_or_else(|_| "db.sqlite3".to_string());
    let conn = Connection::open(db_path)?;
    conn.execute(
        "CREATE TABLE IF NOT EXISTS associations (
            id INTEGER PRIMARY KEY,
            credit_card TEXT NOT NULL,
            phone TEXT NOT NULL
        )",
        [],
    )?;
    Ok(conn)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env::set_var("RUST_LOG", "actix_web=info");
    env_logger::init();

    HttpServer::new(|| {
        App::new()
            .service(associate_card)
            .service(retrieve_cards)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}