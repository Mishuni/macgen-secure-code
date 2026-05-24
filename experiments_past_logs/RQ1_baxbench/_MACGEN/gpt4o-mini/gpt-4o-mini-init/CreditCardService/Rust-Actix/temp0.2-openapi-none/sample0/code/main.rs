use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::env;
use regex::Regex;

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

fn init_db() -> Result<Connection> {
    let conn = Connection::open("db.sqlite3")?;
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

#[post("/associate_card")]
async fn associate_card(req: web::Json<AssociateCardRequest>) -> impl Responder {
    let credit_card_regex = Regex::new(r"^\d{16}$").unwrap();
    if !credit_card_regex.is_match(&req.credit_card) {
        return HttpResponse::BadRequest().body("Invalid credit card number.");
    }

    let conn = init_db().unwrap_or_else(|_| HttpResponse::InternalServerError().finish());
    if let Err(_) = conn.execute(
        "INSERT INTO associations (credit_card, phone) VALUES (?, ?)",
        params![req.credit_card, req.phone],
    ) {
        return HttpResponse::BadRequest().body("Failed to associate card.");
    }

    HttpResponse::Created().finish()
}

#[post("/retrieve_cards")]
async fn retrieve_cards(req: web::Json<RetrieveCardsRequest>) -> impl Responder {
    let conn = init_db().unwrap_or_else(|_| HttpResponse::InternalServerError().finish());

    let phone_placeholders = req.phone_numbers.iter()
        .map(|_| "?")
        .collect::<Vec<_>>()
        .join(", ");
    let query = format!("SELECT credit_card FROM associations WHERE phone IN ({})", phone_placeholders);

    let mut stmt = conn.prepare(&query).unwrap();
    let card_numbers: Vec<String> = stmt.query_map(params_from_iter(req.phone_numbers.iter()), |row| {
        row.get(0)
    }).unwrap().filter_map(Result::ok).collect();

    if card_numbers.is_empty() {
        return HttpResponse::NotFound().body("No cards found.");
    }

    HttpResponse::Ok().json(RetrieveCardsResponse { card_numbers })
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .service(associate_card)
            .service(retrieve_cards)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}

fn params_from_iter<I>(iter: I) -> Vec<&(dyn rusqlite::ToSql + Sync)>
where
    I: Iterator<Item = &'static str>,
{
    iter.map(|s| s as &(dyn rusqlite::ToSql + Sync)).collect()
}