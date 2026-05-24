use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::sync::Mutex;

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
    summary: String,
}

struct AppState {
    db: Mutex<Connection>,
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS entries (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            last_modified_by TEXT NOT NULL,
            last_modified_at TEXT NOT NULL
        )",
        [],
    ).unwrap();

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

async fn get_entries(data: web::Data<AppState>) -> impl Responder {
    let db = data.db.lock().unwrap();
    let mut stmt = db.prepare("SELECT id, title FROM entries").unwrap();
    let entries_iter = stmt.query_map([], |row| {
        Ok(Entry {
            id: row.get(0)?,
            title: row.get(1)?,
            content: "".to_string(),
            last_modified_by: "".to_string(),
            last_modified_at: "".to_string(),
        })
    }).unwrap();

    let mut entries = String::new();
    for entry in entries_iter {
        let entry = entry.unwrap();
        entries.push_str(&format!("<a href=\"/entries/{}\">{}</a><br>", entry.id, entry.title));
    }

    HttpResponse::Ok().content_type("text/html").body(entries)
}

async fn create_entry(new_entry: web::Json<NewEntry>, data: web::Data<AppState>) -> impl Responder {
    let db = data.db.lock().unwrap();
    let id = uuid::Uuid::new_v4().to_string();
    let last_modified_at = chrono::Utc::now().to_rfc3339();

    db.execute(
        "INSERT INTO entries (id, title, content, last_modified_by, last_modified_at) VALUES (?1, ?2, ?3, ?4, ?5)",
        params![id, new_entry.title, new_entry.content, new_entry.created_by, last_modified_at],
    ).unwrap();

    HttpResponse::Created().json(Entry {
        id,
        title: new_entry.title.clone(),
        content: new_entry.content.clone(),
        last_modified_by: new_entry.created_by.clone(),
        last_modified_at,
    })
}

async fn get_entry(web::Path(entry_id): web::Path<String>, data: web::Data<AppState>) -> impl Responder {
    let db = data.db.lock().unwrap();
    let mut stmt = db.prepare("SELECT id, title, content, last_modified_by, last_modified_at FROM entries WHERE id = ?1").unwrap();
    let entry = stmt.query_row(params![entry_id], |row| {
        Ok(Entry {
            id: row.get(0)?,
            title: row.get(1)?,
            content: row.get(2)?,
            last_modified_by: row.get(3)?,
            last_modified_at: row.get(4)?,
        })
    }).optional().unwrap();

    match entry {
        Some(entry) => {
            let response = format!("<h1>{}</h1><p>{}</p><p>Last modified by: {} at {}</p>",
                entry.title, entry.content, entry.last_modified_by, entry.last_modified_at);
            HttpResponse::Ok().content_type("text/html").body(response)
        },
        None => HttpResponse::NotFound().finish(),
    }
}

async fn update_entry(web::Path(entry_id): web::Path<String>, update_entry: web::Json<UpdateEntry>, data: web::Data<AppState>) -> impl Responder {
    let db = data.db.lock().unwrap();
    let last_modified_at = chrono::Utc::now().to_rfc3339();

    let updated_rows = db.execute(
        "UPDATE entries SET content = ?1, last_modified_by = ?2, last_modified_at = ?3 WHERE id = ?4",
        params![update_entry.content, update_entry.modified_by, last_modified_at, entry_id],
    ).unwrap();

    if updated_rows > 0 {
        HttpResponse::Ok().json(Entry {
            id: entry_id,
            title: "".to_string(),
            content: update_entry.content.clone(),
            last_modified_by: update_entry.modified_by.clone(),
            last_modified_at,
        })
    } else {
        HttpResponse::NotFound().finish()
    }
}

async fn get_entry_edits(web::Path(entry_id): web::Path<String>, data: web::Data<AppState>) -> impl Responder {
    // Placeholder for edit history retrieval logic
    HttpResponse::Ok().content_type("text/html").body(format!("Edit history for entry: {}", entry_id))
}