use actix_web::{web, App, HttpServer, HttpResponse, Responder};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection};
use std::env;
use uuid::Uuid;
use chrono::NaiveDateTime;

#[derive(Serialize, Deserialize)]
struct Click {
    id: String,
    timestamp: String,
}

#[derive(Deserialize)]
struct RetrieveClicksQuery {
    date: String,
    direction: String,
}

async fn register_click(conn: web::Data<Connection>) -> impl Responder {
    let id = Uuid::new_v4().to_string();
    let timestamp = chrono::Utc::now().naive_utc().to_string();

    let query = "INSERT INTO clicks (id, timestamp) VALUES (?1, ?2)";
    if let Err(err) = conn.execute(query, params![id, timestamp]) {
        eprintln!("Database error: {}", err);
        return HttpResponse::InternalServerError().finish();
    }

    HttpResponse::Created().finish()
}

async fn retrieve_clicks(
    conn: web::Data<Connection>,
    query: web::Query<RetrieveClicksQuery>,
) -> impl Responder {
    let date = match NaiveDateTime::parse_from_str(&query.date, "%Y-%m-%d") {
        Ok(d) => d,
        Err(_) => return HttpResponse::BadRequest().body("Invalid date format"),
    };

    let valid_directions = ["<", ">", "<=", ">="];
    if !valid_directions.contains(&query.direction.as_str()) {
        return HttpResponse::BadRequest().body("Invalid direction");
    }

    let sql = format!(
        "SELECT id, timestamp FROM clicks WHERE timestamp {} ? ORDER BY timestamp",
        query.direction
    );

    let mut stmt = match conn.prepare(&sql) {
        Ok(s) => s,
        Err(err) => {
            eprintln!("Database error: {}", err);
            return HttpResponse::InternalServerError().finish();
        }
    };

    let rows = match stmt.query_map(params![date.to_string()], |row| {
        Ok(Click {
            id: row.get(0)?,
            timestamp: row.get(1)?,
        })
    }) {
        Ok(r) => r,
        Err(err) => {
            eprintln!("Database error: {}", err);
            return HttpResponse::InternalServerError().finish();
        }
    };

    let mut clicks = Vec::new();
    for row in rows {
        match row {
            Ok(click) => clicks.push(click),
            Err(err) => {
                eprintln!("Database error: {}", err);
                return HttpResponse::InternalServerError().finish();
            }
        }
    }

    if clicks.is_empty() {
        return HttpResponse::NotFound().body("No clicks found");
    }

    HttpResponse::Ok().json(clicks)
}

fn init_db() -> Connection {
    let conn = Connection::open("db.sqlite3").expect("Failed to open database");
    conn.execute(
        "CREATE TABLE IF NOT EXISTS clicks (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL
        )",
        [],
    )
    .expect("Failed to create table");
    conn
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();

    let conn = init_db();
    let conn_data = web::Data::new(conn);

    HttpServer::new(move || {
        App::new()
            .app_data(conn_data.clone())
            .route("/click", web::post().to(register_click))
            .route("/clicks", web::get().to(retrieve_clicks))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}