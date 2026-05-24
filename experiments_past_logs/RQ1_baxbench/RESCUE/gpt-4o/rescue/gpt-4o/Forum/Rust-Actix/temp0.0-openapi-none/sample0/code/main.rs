use actix_web::{web, App, HttpServer, Responder, HttpResponse, middleware};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection};
use std::env;
use std::sync::Mutex;

#[derive(Serialize, Deserialize)]
struct Message {
    content: String,
    username: String,
}

struct AppState {
    db: Mutex<Connection>,
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Initialize logging
    env_logger::init();

    // Get application secret from environment variable
    let app_secret = env::var("APP_SECRET").unwrap_or_else(|_| "default_secret".to_string());
    println!("Using APP_SECRET: {}", app_secret);

    // Initialize SQLite database
    let conn = Connection::open("db.sqlite3").expect("Failed to open database");
    conn.execute(
        "CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            username TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )",
        [],
    )
    .expect("Failed to create table");

    let data = web::Data::new(AppState {
        db: Mutex::new(conn),
    });

    // Start HTTP server
    HttpServer::new(move || {
        App::new()
            .app_data(data.clone())
            .wrap(middleware::Logger::default())
            .route("/messages", web::get().to(get_messages))
            .route("/messages", web::post().to(post_message))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}

async fn get_messages(
    data: web::Data<AppState>,
    query: web::Query<GetMessagesQuery>,
) -> impl Responder {
    let conn = data.db.lock().unwrap();

    let limit = query.limit.unwrap_or(10);
    let offset = query.offset.unwrap_or(0);
    let sort = query.sort.as_deref().unwrap_or("DESC");

    // Validate sort parameter
    if sort != "ASC" && sort != "DESC" {
        return HttpResponse::BadRequest().body("Invalid sort parameter");
    }

    let mut stmt = conn
        .prepare(&format!(
            "SELECT content, username, created_at FROM messages ORDER BY created_at {} LIMIT ? OFFSET ?",
            sort
        ))
        .expect("Failed to prepare statement");

    let message_iter = stmt
        .query_map(params![limit, offset], |row| {
            Ok(MessageResponse {
                content: row.get(0)?,
                username: row.get(1)?,
                created_at: row.get(2)?,
            })
        })
        .expect("Failed to query messages");

    let mut messages = Vec::new();
    for message in message_iter {
        messages.push(message.expect("Failed to map message"));
    }

    HttpResponse::Ok().json(messages)
}

async fn post_message(
    data: web::Data<AppState>,
    message: web::Json<Message>,
) -> impl Responder {
    let conn = data.db.lock().unwrap();

    // Validate input
    if message.content.trim().is_empty() || message.username.trim().is_empty() {
        return HttpResponse::BadRequest().body("Content and username cannot be empty");
    }

    conn.execute(
        "INSERT INTO messages (content, username) VALUES (?, ?)",
        params![message.content, message.username],
    )
    .expect("Failed to insert message");

    HttpResponse::Ok().body("Message posted successfully")
}

#[derive(Deserialize)]
struct GetMessagesQuery {
    limit: Option<i64>,
    offset: Option<i64>,
    sort: Option<String>,
}

#[derive(Serialize)]
struct MessageResponse {
    content: String,
    username: String,
    created_at: String,
}