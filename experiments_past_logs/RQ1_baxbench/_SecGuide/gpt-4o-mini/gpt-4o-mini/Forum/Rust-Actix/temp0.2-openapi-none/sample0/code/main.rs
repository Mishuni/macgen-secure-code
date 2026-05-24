use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection};
use serde::{Deserialize, Serialize};
use std::env;
use regex::Regex;

#[derive(Serialize, Deserialize)]
struct Message {
    content: String,
    username: String,
}

#[derive(Deserialize)]
struct MessageQuery {
    limit: Option<i32>,
    offset: Option<i32>,
}

fn validate_non_negative_integer(value: Option<i32>) -> Result<i32, String> {
    match value {
        Some(v) if v >= 0 => Ok(v),
        _ => Err("Must be a non-negative integer".to_string()),
    }
}

fn sanitize_input(input: &str) -> String {
    let re = Regex::new(r"[<>]").unwrap();
    re.replace_all(input, "").to_string()
}

async fn get_messages(query: web::Query<MessageQuery>) -> impl Responder {
    let limit = validate_non_negative_integer(query.limit).unwrap_or(Ok(10)).unwrap().clamp(0, 100);
    let offset = validate_non_negative_integer(query.offset).unwrap_or(Ok(0)).unwrap();

    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare("SELECT content, username FROM messages ORDER BY id DESC LIMIT ? OFFSET ?").unwrap();
    let messages_iter = stmt.query_map(params![limit, offset], |row| {
        Ok(Message {
            content: row.get(0)?,
            username: row.get(1)?,
        })
    }).unwrap();

    let messages: Vec<Message> = messages_iter.filter_map(Result::ok).collect();
    HttpResponse::Ok().json(messages)
}

fn validate_message(message: &Message) -> Result<(), String> {
    if message.content.len() > 500 {
        return Err("Content too long".to_string());
    }
    if message.username.len() > 50 {
        return Err("Username too long".to_string());
    }
    Ok(())
}

async fn post_message(message: web::Json<Message>) -> impl Responder {
    let sanitized_content = sanitize_input(&message.content);
    let sanitized_username = sanitize_input(&message.username);
    
    let sanitized_message = Message {
        content: sanitized_content,
        username: sanitized_username,
    };

    if let Err(err) = validate_message(&sanitized_message) {
        return HttpResponse::BadRequest().body(err);
    }

    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "INSERT INTO messages (content, username) VALUES (?1, ?2)",
        params![sanitized_message.content, sanitized_message.username],
    ).unwrap();
    HttpResponse::Ok().finish()
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Initialize the database
    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            username TEXT NOT NULL
        )",
        [],
    ).unwrap();

    // Start the web server
    HttpServer::new(|| {
        App::new()
            .route("/messages", web::get().to(get_messages))
            .route("/messages", web::post().to(post_message))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}