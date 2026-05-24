use actix_web::{web, App, HttpServer, HttpResponse, Responder};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
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

async fn associate_card(req: web::Json<AssociateCardRequest>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").expect("Failed to open database");
    let result = conn.execute(
        "INSERT INTO card_phone (credit_card, phone) VALUES (?1, ?2)",
        params![req.credit_card, req.phone],
    );

    match result {
        Ok(_) => HttpResponse::Created().finish(),
        Err(_) => HttpResponse::BadRequest().finish(),
    }
}

async fn retrieve_cards(req: web::Json<RetrieveCardsRequest>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").expect("Failed to open database");
    let mut stmt = conn
        .prepare(
            "SELECT credit_card FROM card_phone WHERE phone IN ("
                .to_owned()
                + &req.phone_numbers.iter().map(|_| "?").collect::<Vec<_>>().join(", ")
                + ") GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?",
        )
        .expect("Failed to prepare statement");

    let card_iter = stmt
        .query_map(
            params_from_iter(req.phone_numbers.iter().chain(std::iter::once(&req.phone_numbers.len()))),
            |row| row.get(0),
        )
        .expect("Failed to query database");

    let card_numbers: Vec<String> = card_iter.filter_map(Result::ok).collect();

    if card_numbers.is_empty() {
        HttpResponse::NotFound().finish()
    } else {
        HttpResponse::Ok().json(RetrieveCardsResponse { card_numbers })
    }
}

fn init_db() {
    let conn = Connection::open("db.sqlite3").expect("Failed to open database");
    conn.execute(
        "CREATE TABLE IF NOT EXISTS card_phone (
            id INTEGER PRIMARY KEY,
            credit_card TEXT NOT NULL,
            phone TEXT NOT NULL
        )",
        [],
    )
    .expect("Failed to create table");
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env::set_var("RUST_LOG", "actix_web=info");
    env_logger::init();

    init_db();

    HttpServer::new(|| {
        App::new()
            .route("/associate_card", web::post().to(associate_card))
            .route("/retrieve_cards", web::post().to(retrieve_cards))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}