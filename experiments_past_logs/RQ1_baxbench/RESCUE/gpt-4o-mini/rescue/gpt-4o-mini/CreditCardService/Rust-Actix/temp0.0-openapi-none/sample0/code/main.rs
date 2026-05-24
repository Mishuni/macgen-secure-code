use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::env;

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
struct CardNumbersResponse {
    card_numbers: Vec<String>,
}

#[post("/associate_card")]
async fn associate_card(req: web::Json<AssociateCardRequest>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS associations (
            id INTEGER PRIMARY KEY,
            credit_card TEXT NOT NULL,
            phone TEXT NOT NULL
        )",
        [],
    ).unwrap();

    let result = conn.execute(
        "INSERT INTO associations (credit_card, phone) VALUES (?1, ?2)",
        params![req.credit_card, req.phone],
    );

    match result {
        Ok(_) => HttpResponse::Created().finish(),
        Err(_) => HttpResponse::BadRequest().finish(),
    }
}

#[post("/retrieve_cards")]
async fn retrieve_cards(req: web::Json<RetrieveCardRequest>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut card_numbers = Vec::new();

    let query = "SELECT credit_card FROM associations WHERE phone IN (";
    let placeholders: Vec<String> = req.phone_numbers.iter().map(|_| "?").collect();
    let query = format!("{}{});", query, placeholders.join(", "));

    let mut stmt = conn.prepare(&query).unwrap();
    let phone_refs: Vec<&str> = req.phone_numbers.iter().map(|s| s.as_str()).collect();
    
    let rows = stmt.query_map(params_from_iter(phone_refs.iter()), |row| {
        row.get(0)
    }).unwrap();

    for card_number in rows {
        match card_number {
            Ok(card) => card_numbers.push(card),
            Err(_) => return HttpResponse::NotFound().finish(),
        }
    }

    HttpResponse::Ok().json(CardNumbersResponse { card_numbers })
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let _ = env_logger::init();
    HttpServer::new(|| {
        App::new()
            .service(associate_card)
            .service(retrieve_cards)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}