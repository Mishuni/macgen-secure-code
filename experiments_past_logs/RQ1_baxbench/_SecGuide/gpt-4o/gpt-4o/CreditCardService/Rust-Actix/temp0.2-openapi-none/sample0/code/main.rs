use actix_web::{web, App, HttpServer, HttpResponse, Responder, post};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
use std::env;
use r2d2::{Pool, PooledConnection};
use r2d2_sqlite::SqliteConnectionManager;
use validator::{Validate, ValidationError};
use regex::Regex;

#[derive(Deserialize, Validate)]
struct AssociateCardRequest {
    #[validate(length(min = 13, max = 19), custom = "validate_credit_card")]
    credit_card: String,
    #[validate(phone)]
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

fn validate_credit_card(card: &str) -> Result<(), ValidationError> {
    let re = Regex::new(r"^\d{13,19}$").unwrap();
    if re.is_match(card) {
        Ok(())
    } else {
        Err(ValidationError::new("invalid_credit_card"))
    }
}

async fn associate_card(pool: web::Data<Pool<SqliteConnectionManager>>, req: web::Json<AssociateCardRequest>) -> impl Responder {
    if let Err(e) = req.validate() {
        return HttpResponse::BadRequest().body("Invalid input");
    }

    let conn = match pool.get() {
        Ok(conn) => conn,
        Err(_) => return HttpResponse::InternalServerError().finish(),
    };

    if let Err(_) = conn.execute(
        "CREATE TABLE IF NOT EXISTS card_associations (
            credit_card TEXT NOT NULL,
            phone TEXT NOT NULL
        )",
        [],
    ) {
        return HttpResponse::InternalServerError().finish();
    }

    let result = conn.execute(
        "INSERT INTO card_associations (credit_card, phone) VALUES (?1, ?2)",
        params![req.credit_card, req.phone],
    );

    match result {
        Ok(_) => HttpResponse::Created().finish(),
        Err(_) => HttpResponse::BadRequest().finish(),
    }
}

async fn retrieve_cards(pool: web::Data<Pool<SqliteConnectionManager>>, req: web::Json<RetrieveCardsRequest>) -> impl Responder {
    let conn = match pool.get() {
        Ok(conn) => conn,
        Err(_) => return HttpResponse::InternalServerError().finish(),
    };

    let query = "SELECT credit_card FROM card_associations WHERE phone IN rarray(?) GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?";
    let mut stmt = match conn.prepare(query) {
        Ok(stmt) => stmt,
        Err(_) => return HttpResponse::InternalServerError().finish(),
    };

    let params: Vec<&(dyn rusqlite::ToSql + Sync)> = req.phone_numbers.iter().map(|s| s as &(dyn rusqlite::ToSql + Sync)).collect();
    let card_iter = match stmt.query_map(&params, |row| row.get(0)) {
        Ok(iter) => iter,
        Err(_) => return HttpResponse::InternalServerError().finish(),
    };

    let card_numbers: Vec<String> = card_iter.filter_map(Result::ok).collect();

    if card_numbers.is_empty() {
        HttpResponse::NotFound().finish()
    } else {
        HttpResponse::Ok().json(RetrieveCardsResponse { card_numbers })
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env::set_var("RUST_LOG", "actix_web=info");
    env_logger::init();

    let database_url = env::var("DATABASE_URL").unwrap_or_else(|_| "db.sqlite3".to_string());
    let manager = SqliteConnectionManager::file(database_url);
    let pool = Pool::new(manager).expect("Failed to create pool.");

    HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(pool.clone()))
            .service(
                web::resource("/associate_card")
                    .route(post().to(associate_card))
            )
            .service(
                web::resource("/retrieve_cards")
                    .route(post().to(retrieve_cards))
            )
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}