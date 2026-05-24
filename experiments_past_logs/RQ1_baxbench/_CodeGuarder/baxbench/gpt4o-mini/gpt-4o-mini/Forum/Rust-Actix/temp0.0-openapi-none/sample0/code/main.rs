use actix_web::{web, App, HttpServer, HttpResponse, Responder};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::env;

#[derive(Serialize, Deserialize)]
struct Message {
    content: String,
    username: String,
}

async fn get_messages(
    limit: Option<web::Query<i32>>,
    offset: Option<web::Query<i32>>,
    sort: Option<web::Query<String>>,
) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let limit = limit.unwrap_or(web::Query(10)).0;
    let offset = offset.unwrap_or(web::Query(0)).0;
    let sort_order = sort.unwrap_or(web::Query("DESC".to_string())).0;

    let mut stmt = conn.prepare(&format!(
        "SELECT content, username FROM messages ORDER BY id {} LIMIT ? OFFSET ?",
        if sort_order.to_uppercase() == "ASC" { "ASC" } else { "DESC" }
    )).unwrap();

    let messages: Result<Vec<Message>, _> = stmt.query_map(params![limit, offset], |row| {
        Ok(Message {
            content: row.get(0)?,
            username: row.get(1)?,
        })
    }).collect();

    match messages {
        Ok(msgs) => HttpResponse::Ok().json(msgs),
        Err(_) => HttpResponse::InternalServerError().finish(),
    }
}

async fn post_message(message: web::Json<Message>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            username TEXT NOT NULL
        )",
        [],
    ).unwrap();

    conn.execute(
        "INSERT INTO messages (content, username) VALUES (?1, ?2)",
        params![message.content, message.username],
    ).unwrap();

    HttpResponse::Ok().finish()
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let _ = env_logger::init();
    let app_secret = env::var("APP_SECRET").unwrap_or_else(|_| "default_secret".to_string());

    println!("Using APP_SECRET: {}", app_secret);

    HttpServer::new(|| {
        App::new()
            .route("/messages", web::get().to(get_messages))
            .route("/messages", web::post().to(post_message))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}