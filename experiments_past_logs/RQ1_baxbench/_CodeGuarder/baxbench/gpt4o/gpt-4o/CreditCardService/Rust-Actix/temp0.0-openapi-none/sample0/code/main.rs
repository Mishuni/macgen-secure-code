use actix_web::{web, App, HttpServer, HttpResponse, Responder, post};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
use std::env;
use log::{info, error};
use env_logger;

// Data model for associating a credit card with a phone number
#[derive(Deserialize)]
struct AssociateCardRequest {
    credit_card: String,
    phone: String,
}

// Data model for retrieving cards associated with phone numbers
#[derive(Deserialize)]
struct RetrieveCardsRequest {
    phone_numbers: Vec<String>,
}

#[derive(Serialize)]
struct RetrieveCardsResponse {
    card_numbers: Vec<String>,
}

// Initialize SQLite database and create necessary tables
fn init_db() -> Result<Connection> {
    let conn = Connection::open("db.sqlite3")?;
    conn.execute(
        "CREATE TABLE IF NOT EXISTS card_phone_association (
            id INTEGER PRIMARY KEY,
            credit_card TEXT NOT NULL,
            phone TEXT NOT NULL
        )",
        [],
    )?;
    Ok(conn)
}

// Handler for the /associate_card endpoint
#[post("/associate_card")]
async fn associate_card(req: web::Json<AssociateCardRequest>, db: web::Data<Connection>) -> impl Responder {
    let conn = db.get_ref();
    match conn.execute(
        "INSERT INTO card_phone_association (credit_card, phone) VALUES (?1, ?2)",
        params![req.credit_card, req.phone],
    ) {
        Ok(_) => HttpResponse::Created().finish(),
        Err(err) => {
            error!("Failed to associate card: {}", err);
            HttpResponse::BadRequest().body("Invalid request")
        }
    }
}

// Handler for the /retrieve_cards endpoint
#[post("/retrieve_cards")]
async fn retrieve_cards(req: web::Json<RetrieveCardsRequest>, db: web::Data<Connection>) -> impl Responder {
    let conn = db.get_ref();
    let mut stmt = match conn.prepare(
        "SELECT credit_card FROM card_phone_association WHERE phone = ?1"
    ) {
        Ok(stmt) => stmt,
        Err(err) => {
            error!("Failed to prepare statement: {}", err);
            return HttpResponse::InternalServerError().finish();
        }
    };

    let mut card_numbers = Vec::new();
    for phone in &req.phone_numbers {
        let mut rows = match stmt.query(params![phone]) {
            Ok(rows) => rows,
            Err(err) => {
                error!("Failed to query database: {}", err);
                return HttpResponse::InternalServerError().finish();
            }
        };

        while let Ok(Some(row)) = rows.next() {
            let card_number: String = row.get(0).unwrap();
            if !card_numbers.contains(&card_number) {
                card_numbers.push(card_number);
            }
        }
    }

    if card_numbers.is_empty() {
        HttpResponse::NotFound().finish()
    } else {
        HttpResponse::Ok().json(RetrieveCardsResponse { card_numbers })
    }
}

// Main function to set up the Actix web server
#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    let db = init_db().expect("Failed to initialize database");

    info!("Starting server at http://0.0.0.0:5000");
    HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(db.clone()))
            .service(associate_card)
            .service(retrieve_cards)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}