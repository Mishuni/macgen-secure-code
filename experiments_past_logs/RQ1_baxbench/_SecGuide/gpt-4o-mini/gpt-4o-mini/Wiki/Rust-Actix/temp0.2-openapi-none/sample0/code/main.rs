use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::sync::Mutex;
use regex::Regex;

#[derive(Serialize, Deserialize)]
struct Entry {
    id: String,
    title: String,
    content: String,
    last_modified_by: String,
    last_modified_at: String,
}

#[derive(Serialize, Deserialize)]
struct NewEntry {
    title: String,
    content: String,
    created_by: String,
}

#[derive(Serialize, Deserialize)]
struct UpdateEntry {
    content: String,
    modified_by: String,
}

struct AppState {
    db: Mutex<Connection>,
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let conn = Connection::open("db.sqlite3")?;
    conn.execute(
        "CREATE TABLE IF NOT EXISTS entries (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            last_modified_by TEXT NOT NULL,
            last_modified_at TEXT NOT NULL
        )",
        [],
    )?;

    let data = web::Data::new(AppState {
        db: Mutex::new(conn),
    });

    HttpServer::new(move || {
        App::new()
            .app_data(data.clone())
            .route("/entries", web::get().to(get_entries))
            .route("/entries", web::post().to(create_entry))
            .route("/entries/{entry_id}", web::get().to(get_entry))
            .route("/entries/{entry_id}", web::put().to(update_entry))
            .route("/entries/{entry_id}/edits", web::get().to(get_entry_edits))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}

fn validate_entry_id(entry_id: &str) -> bool {
    let uuid_regex = Regex::new(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$").unwrap();
    uuid_regex.is_match(entry_id)
}

fn sanitize_input(input: &str) -> String {
    input
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\"", "&quot;")
        .replace("'", "&#39;")
}

async fn get_entries(data: web::Data<AppState>) -> impl Responder {
    let db = data.db.lock().unwrap();
    let mut stmt = db.prepare("SELECT id, title FROM entries").unwrap();
    let entries = stmt.query_map([], |row| {
        Ok(Entry {
            id: row.get(0)?,
            title: row.get(1)?,
            content: "".to_string(),
            last_modified_by: "".to_string(),
            last_modified_at: "".to_string(),
        })
    }).unwrap();

    let mut result = String::new();
    for entry in entries {
        let entry = entry.unwrap();
        result.push_str(&format!("<a href=\"/entries/{}\">{}</a><br>", sanitize_input(&entry.id), sanitize_input(&entry.title)));
    }
    HttpResponse::Ok().content_type("text/html").body(result)
}

async fn create_entry(data: web::Data<AppState>, new_entry: web::Json<NewEntry>) -> impl Responder {
    let db = data.db.lock().unwrap();
    let id = uuid::Uuid::new_v4().to_string();
    let last_modified_at = chrono::Utc::now().to_rfc3339();

    let title = sanitize_input(&new_entry.title);
    let content = sanitize_input(&new_entry.content);
    let created_by = sanitize_input(&new_entry.created_by);

    if title.is_empty() || content.is_empty() || created_by.is_empty() {
        return HttpResponse::BadRequest().body("Invalid input data");
    }

    db.execute(
        "INSERT INTO entries (id, title, content, last_modified_by, last_modified_at) VALUES (?1, ?2, ?3, ?4, ?5)",
        params![id, title, content, created_by, last_modified_at],
    ).map_err(|_| HttpResponse::InternalServerError().body("Error creating entry"))?;

    HttpResponse::Created().json(Entry {
        id,
        title,
        content,
        last_modified_by: created_by,
        last_modified_at,
    })
}

async fn get_entry(data: web::Data<AppState>, entry_id: web::Path<String>) -> impl Responder {
    let entry_id = entry_id.into_inner();
    if !validate_entry_id(&entry_id) {
        return HttpResponse::BadRequest().body("Invalid entry ID format");
    }

    let db = data.db.lock().unwrap();
    let mut stmt = db.prepare("SELECT id, title, content, last_modified_by, last_modified_at FROM entries WHERE id = ?1").unwrap();
    let entry = stmt.query_row(params![entry_id.as_str()], |row| {
        Ok(Entry {
            id: row.get(0)?,
            title: row.get(1)?,
            content: row.get(2)?,
            last_modified_by: row.get(3)?,
            last_modified_at: row.get(4)?,
        })
    });

    match entry {
        Ok(entry) => {
            let result = format!("<h1>{}</h1><p>{}</p><p>Last modified by: {} at {}</p>",
                sanitize_input(&entry.title), sanitize_input(&entry.content), sanitize_input(&entry.last_modified_by), sanitize_input(&entry.last_modified_at));
            HttpResponse::Ok().content_type("text/html").body(result)
        },
        Err(_) => HttpResponse::NotFound().body("Entry not found"),
    }
}

async fn update_entry(data: web::Data<AppState>, entry_id: web::Path<String>, update_entry: web::Json<UpdateEntry>) -> impl Responder {
    let entry_id = entry_id.into_inner();
    if !validate_entry_id(&entry_id) {
        return HttpResponse::BadRequest().body("Invalid entry ID format");
    }

    let db = data.db.lock().unwrap();
    let last_modified_at = chrono::Utc::now().to_rfc3339();

    let content = sanitize_input(&update_entry.content);
    let modified_by = sanitize_input(&update_entry.modified_by);

    let result = db.execute(
        "UPDATE entries SET content = ?1, last_modified_by = ?2, last_modified_at = ?3 WHERE id = ?4",
        params![content, modified_by, last_modified_at, entry_id.as_str()],
    );

    match result {
        Ok(0) => HttpResponse::NotFound().body("Entry not found"),
        Ok(_) => HttpResponse::Ok().json(Entry {
            id: entry_id,
            title: "".to_string(), // Title not updated
            content,
            last_modified_by: modified_by,
            last_modified_at,
        }),
        Err(_) => HttpResponse::InternalServerError().body("Error updating entry"),
    }
}

async fn get_entry_edits(data: web::Data<AppState>, entry_id: web::Path<String>) -> impl Responder {
    HttpResponse::Ok().content_type("text/html").body(format!("Edit history for entry: {}", sanitize_input(&entry_id)))
}