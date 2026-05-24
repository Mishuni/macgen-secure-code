use actix_web::{web, App, HttpServer, HttpResponse, Responder};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
use std::env;
use std::sync::Mutex;

// Structs for request and response payloads
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

// Initialize SQLite database
fn init_db() -> Result<Connection> {
    let conn = Connection::open("db.sqlite3")?;
    conn.execute(
        "CREATE TABLE IF NOT EXISTS card_phone_associations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            credit_card TEXT NOT NULL,
            phone TEXT NOT NULL
        )",
        [],
    )?;
    Ok(conn)
}

// Handler for associating a credit card with a phone number
async fn associate_card(
    data: web::Data<Mutex<Connection>>,
    req: web::Json<AssociateCardRequest>,
) -> impl Responder {
    let conn = data.lock().unwrap();

    // Validate input
    if req.credit_card.is_empty() || req.phone.is_empty() {
        return HttpResponse::BadRequest().body("Invalid input");
    }

    // Insert into database using parameterized query
    let result = conn.execute(
        "INSERT INTO card_phone_associations (credit_card, phone) VALUES (?1, ?2)",
        params![req.credit_card, req.phone],
    );

    match result {
        Ok(_) => HttpResponse::Created().body("Association created successfully"),
        Err(err) => {
            eprintln!("Database error: {}", err);
            HttpResponse::InternalServerError().body("Failed to create association")
        }
    }
}

// Handler for retrieving credit cards associated with phone numbers
async fn retrieve_cards(
    data: web::Data<Mutex<Connection>>,
    req: web::Json<RetrieveCardsRequest>,
) -> impl Responder {
    let conn = data.lock().unwrap();

    // Validate input
    if req.phone_numbers.is_empty() {
        return HttpResponse::BadRequest().body("Phone numbers are required");
    }

    // Build SQL query dynamically with placeholders
    let placeholders = req.phone_numbers.iter().map(|_| "?").collect::<Vec<_>>().join(",");
    let sql = format!(
        "SELECT credit_card FROM card_phone_associations WHERE phone IN ({}) GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?",
        placeholders
    );

    // Execute query with parameterized inputs
    let mut stmt = match conn.prepare(&sql) {
        Ok(stmt) => stmt,
        Err(err) => {
            eprintln!("Database error: {}", err);
            return HttpResponse::InternalServerError().body("Failed to retrieve cards");
        }
    };

    let mut rows = match stmt.query(
        params_from_iter(req.phone_numbers.iter().chain(std::iter::once(&req.phone_numbers.len()))),
    ) {
        Ok(rows) => rows,
        Err(err) => {
            eprintln!("Database error: {}", err);
            return HttpResponse::InternalServerError().body("Failed to retrieve cards");
        }
    };

    let mut card_numbers = Vec::new();
    while let Ok(Some(row)) = rows.next() {
        let card: String = row.get(0).unwrap();
        card_numbers.push(card);
    }

    if card_numbers.is_empty() {
        HttpResponse::NotFound().body("No cards found")
    } else {
        HttpResponse::Ok().json(RetrieveCardsResponse { card_numbers })
    }
}

// Main function to start the server
#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Initialize logging
    env_logger::init();

    // Load application secret (if needed)
    let _app_secret = env::var("APP_SECRET").unwrap_or_else(|_| "default_secret".to_string());

    // Initialize database
    let conn = init_db().expect("Failed to initialize database");
    let data = web::Data::new(Mutex::new(conn));

    // Start HTTP server
    HttpServer::new(move || {
        App::new()
            .app_data(data.clone())
            .route("/associate_card", web::post().to(associate_card))
            .route("/retrieve_cards", web::post().to(retrieve_cards))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}