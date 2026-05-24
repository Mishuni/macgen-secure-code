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
struct RetrieveCardsRequest {
    phone_numbers: Vec<String>,
}

#[derive(Serialize)]
struct RetrieveCardsResponse {
    card_numbers: Vec<String>,
}

#[post("/associate_card")]
async fn associate_card(req: web::Json<AssociateCardRequest>) -> impl Responder {
    if !is_valid_credit_card(&req.credit_card) || !is_valid_phone(&req.phone) {
        return HttpResponse::BadRequest().finish();
    }

    let conn = establish_connection();
    match conn.execute(
        "INSERT INTO associations (credit_card, phone) VALUES (?1, ?2)",
        params![req.credit_card, req.phone],
    ) {
        Ok(_) => HttpResponse::Created().finish(),
        Err(_) => HttpResponse::BadRequest().finish(),
    }
}

#[post("/retrieve_cards")]
async fn retrieve_cards(req: web::Json<RetrieveCardsRequest>) -> impl Responder {
    if req.phone_numbers.is_empty() || !req.phone_numbers.iter().all(|p| is_valid_phone(p)) {
        return HttpResponse::BadRequest().finish();
    }

    let conn = establish_connection();
    let mut card_numbers = Vec::new();

    let query = format!(
        "SELECT DISTINCT credit_card FROM associations WHERE phone IN ({}) GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?",
        req.phone_numbers.iter().map(|_| "?").collect::<Vec<_>>().join(", ")
    );

    let mut stmt = match conn.prepare(&query) {
        Ok(stmt) => stmt,
        Err(_) => return HttpResponse::BadRequest().finish(),
    };

    let phone_count = req.phone_numbers.len();
    let params: Vec<&(dyn rusqlite::ToSql + Sync)> = req.phone_numbers.iter().map(|p| p as &dyn rusqlite::ToSql).collect();

    let rows = stmt.query_map(params![&params[..], phone_count], |row| row.get(0));

    match rows {
        Ok(rows) => {
            for row in rows {
                match row {
                    Ok(card_number) => card_numbers.push(card_number),
                    Err(_) => return HttpResponse::NotFound().finish(),
                }
            }
            HttpResponse::Ok().json(RetrieveCardsResponse { card_numbers })
        }
        Err(_) => HttpResponse::BadRequest().finish(),
    }
}

fn is_valid_credit_card(card: &str) -> bool {
    // Simple validation: check if the card is numeric and has 13 to 19 digits
    card.chars().all(char::is_numeric) && (13..=19).contains(&card.len())
}

fn is_valid_phone(phone: &str) -> bool {
    // Simple validation: check if the phone is in a valid format (e.g., digits and dashes)
    phone.chars().all(|c| c.is_numeric() || c == '-') && !phone.is_empty()
}

fn establish_connection() -> Connection {
    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS associations (
            id INTEGER PRIMARY KEY,
            credit_card TEXT NOT NULL,
            phone TEXT NOT NULL
        )",
        [],
    ).unwrap();
    conn
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env::var("APP_SECRET").expect("APP_SECRET must be set");
    HttpServer::new(|| {
        App::new()
            .service(associate_card)
            .service(retrieve_cards)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}