use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::env;
use log::{error, info};

#[derive(Serialize, Deserialize)]
struct AssociateCardRequest {
    credit_card: String,
    phone: String,
}

#[derive(Serialize, Deserialize)]
struct RetrieveCardsRequest {
    phone_numbers: Vec<String>,
}

#[derive(Serialize)]
struct RetrieveCardsResponse {
    card_numbers: Vec<String>,
}

async fn associate_card(
    req: web::Json<AssociateCardRequest>,
    db: web::Data<Connection>,
) -> impl Responder {
    let credit_card = &req.credit_card;
    let phone = &req.phone;

    if credit_card.is_empty() || phone.is_empty() {
        return HttpResponse::BadRequest().body("Invalid request");
    }

    match db.execute(
        "INSERT INTO associations (credit_card, phone) VALUES (?1, ?2)",
        params![credit_card, phone],
    ) {
        Ok(_) => HttpResponse::Created().finish(),
        Err(err) => {
            error!("Database error: {}", err);
            HttpResponse::InternalServerError().body("Internal server error")
        }
    }
}

async fn retrieve_cards(
    req: web::Json<RetrieveCardsRequest>,
    db: web::Data<Connection>,
) -> impl Responder {
    let phone_numbers = &req.phone_numbers;

    if phone_numbers.is_empty() {
        return HttpResponse::BadRequest().body("Invalid request");
    }

    let mut card_numbers = Vec::new();
    let query = format!(
        "SELECT credit_card FROM associations WHERE phone IN ({}) GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?",
        phone_numbers.iter().map(|_| "?").collect::<Vec<_>>().join(", ")
    );

    let mut stmt = match db.prepare(&query) {
        Ok(stmt) => stmt,
        Err(err) => {
            error!("Database error: {}", err);
            return HttpResponse::InternalServerError().body("Internal server error");
        }
    };

    let phone_count = phone_numbers.len() as i32;

    match stmt.query(params_from_iter(phone_numbers.iter().chain(std::iter::once(&phone_count)))) {
        Ok(rows) => {
            for row in rows {
                if let Ok(credit_card) = row {
                    card_numbers.push(credit_card.get(0).unwrap());
                }
            }
            HttpResponse::Ok().json(RetrieveCardsResponse { card_numbers })
        }
        Err(err) => {
            error!("Database error: {}", err);
            HttpResponse::InternalServerError().body("Internal server error")
        }
    }
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

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    let db = init_db().expect("Failed to initialize database");

    HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(db.clone()))
            .route("/associate_card", web::post().to(associate_card))
            .route("/retrieve_cards", web::post().to(retrieve_cards))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}