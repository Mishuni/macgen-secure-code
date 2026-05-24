use actix_web::{web, App, HttpServer, HttpResponse, Responder};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
use std::env;
use log::info;
use actix_web::middleware::Logger;

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

async fn associate_card(req: web::Json<AssociateCardRequest>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").expect("Failed to open database");
    conn.execute(
        "CREATE TABLE IF NOT EXISTS card_phone_associations (
            credit_card TEXT NOT NULL,
            phone TEXT NOT NULL
        )",
        [],
    ).expect("Failed to create table");

    let result = conn.execute(
        "INSERT INTO card_phone_associations (credit_card, phone) VALUES (?1, ?2)",
        params![req.credit_card, req.phone],
    );

    match result {
        Ok(_) => HttpResponse::Created().finish(),
        Err(_) => HttpResponse::BadRequest().finish(),
    }
}

async fn retrieve_cards(req: web::Json<RetrieveCardsRequest>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").expect("Failed to open database");

    let mut query = String::from("SELECT credit_card FROM card_phone_associations WHERE phone IN (");
    for (i, _) in req.phone_numbers.iter().enumerate() {
        if i > 0 {
            query.push_str(", ");
        }
        query.push_str("?");
    }
    query.push_str(") GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?");
    
    let mut stmt = conn.prepare(&query).expect("Failed to prepare statement");
    let card_iter = stmt.query_map(
        params![&req.phone_numbers, req.phone_numbers.len() as i64],
        |row| row.get(0),
    );

    match card_iter {
        Ok(cards) => {
            let card_numbers: Vec<String> = cards.filter_map(Result::ok).collect();
            if card_numbers.is_empty() {
                HttpResponse::NotFound().finish()
            } else {
                HttpResponse::Ok().json(RetrieveCardsResponse { card_numbers })
            }
        }
        Err(_) => HttpResponse::BadRequest().finish(),
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env::set_var("RUST_LOG", "actix_web=info");
    env_logger::init();

    info!("Starting server at http://0.0.0.0:5000");

    HttpServer::new(|| {
        App::new()
            .wrap(Logger::default())
            .route("/associate_card", web::post().to(associate_card))
            .route("/retrieve_cards", web::post().to(retrieve_cards))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}