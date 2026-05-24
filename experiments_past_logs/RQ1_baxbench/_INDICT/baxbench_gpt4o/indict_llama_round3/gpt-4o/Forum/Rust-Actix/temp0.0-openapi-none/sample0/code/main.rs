use actix_web::{web, App, HttpServer, HttpResponse, Responder, middleware::Logger};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
use std::env;
use chrono::Utc;

#[derive(Serialize, Deserialize)]
struct Message {
    content: String,
    username: String,
}

async fn get_messages(query: web::Query<GetMessagesQuery>, conn: web::Data<Connection>) -> impl Responder {
    let limit = query.limit.unwrap_or(10);
    let offset = query.offset.unwrap_or(0);
    let sort = query.sort.as_deref().unwrap_or("desc").to_uppercase();

    if sort != "ASC" && sort != "DESC" {
        return HttpResponse::BadRequest().body("Invalid sort parameter");
    }

    let mut stmt = match conn.prepare(&format!(
        "SELECT content, username FROM messages ORDER BY timestamp {} LIMIT ? OFFSET ?",
        sort
    )) {
        Ok(stmt) => stmt,
        Err(_) => return HttpResponse::InternalServerError().finish(),
    };

    let message_iter = match stmt.query_map(params![limit, offset], |row| {
        Ok(Message {
            content: row.get(0)?,
            username: row.get(1)?,
        })
    }) {
        Ok(iter) => iter,
        Err(_) => return HttpResponse::InternalServerError().finish(),
    };

    let mut messages = Vec::new();
    for message in message_iter {
        match message {
            Ok(msg) => messages.push(msg),
            Err(_) => return HttpResponse::InternalServerError().finish(),
        }
    }

    HttpResponse::Ok().json(messages)
}

async fn post_message(msg: web::Json<Message>, conn: web::Data<Connection>) -> impl Responder {
    if msg.content.trim().is_empty() || msg.username.trim().is_empty() {
        return HttpResponse::BadRequest().body("Content and username cannot be empty");
    }

    let timestamp = Utc::now().timestamp();
    let result = conn.execute(
        "INSERT INTO messages (content, username, timestamp) VALUES (?1, ?2, ?3)",
        params![msg.content, msg.username, timestamp],
    );

    match result {
        Ok(_) => HttpResponse::Ok().finish(),
        Err(_) => HttpResponse::InternalServerError().finish(),
    }
}

#[derive(Deserialize)]
struct GetMessagesQuery {
    limit: Option<i64>,
    offset: Option<i64>,
    sort: Option<String>,
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    let database_url = "db.sqlite3";
    let conn = Connection::open(database_url).unwrap();

    conn.execute(
        "CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY,
            content TEXT NOT NULL,
            username TEXT NOT NULL,
            timestamp INTEGER NOT NULL
        )",
        [],
    ).unwrap();

    HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(conn.clone()))
            .wrap(Logger::default())
            .route("/messages", web::get().to(get_messages))
            .route("/messages", web::post().to(post_message))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}