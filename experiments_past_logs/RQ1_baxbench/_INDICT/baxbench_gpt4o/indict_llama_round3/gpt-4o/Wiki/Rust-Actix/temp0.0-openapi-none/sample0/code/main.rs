use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use chrono::Utc;
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::sync::Mutex;
use uuid::Uuid;

#[derive(Serialize, Deserialize)]
struct Entry {
    id: String,
    title: String,
    content: String,
    last_modified_by: String,
    last_modified_at: String,
}

#[derive(Deserialize)]
struct NewEntry {
    title: String,
    content: String,
    created_by: String,
}

#[derive(Deserialize)]
struct UpdateEntry {
    content: String,
    modified_by: String,
    summary: String,
}

struct AppState {
    db: Mutex<Connection>,
}

async fn get_entries(data: web::Data<AppState>) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let mut stmt = conn.prepare("SELECT id, title FROM entries").unwrap();
    let entry_iter = stmt
        .query_map([], |row| {
            Ok(Entry {
                id: row.get(0)?,
                title: row.get(1)?,
                content: String::new(),
                last_modified_by: String::new(),
                last_modified_at: String::new(),
            })
        })
        .unwrap();

    let mut entries = Vec::new();
    for entry in entry_iter {
        entries.push(entry.unwrap());
    }

    HttpResponse::Ok().json(entries)
}

async fn create_entry(
    data: web::Data<AppState>,
    new_entry: web::Json<NewEntry>,
) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let id = Uuid::new_v4().to_string();
    let now = Utc::now().to_rfc3339();

    conn.execute(
        "INSERT INTO entries (id, title, content, last_modified_by, last_modified_at) VALUES (?1, ?2, ?3, ?4, ?5)",
        params![id, new_entry.title, new_entry.content, new_entry.created_by, now],
    )
    .unwrap();

    conn.execute(
        "INSERT INTO edits (entry_id, content, last_modified_by, last_modified_at) VALUES (?1, ?2, ?3, ?4)",
        params![id, new_entry.content, new_entry.created_by, now],
    )
    .unwrap();

    HttpResponse::Created().json(Entry {
        id,
        title: new_entry.title.clone(),
        content: new_entry.content.clone(),
        last_modified_by: new_entry.created_by.clone(),
        last_modified_at: now,
    })
}

async fn get_entry(data: web::Data<AppState>, entry_id: web::Path<String>) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let mut stmt = conn
        .prepare("SELECT id, title, content, last_modified_by, last_modified_at FROM entries WHERE id = ?1")
        .unwrap();

    let entry = stmt
        .query_row(params![entry_id.into_inner()], |row| {
            Ok(Entry {
                id: row.get(0)?,
                title: row.get(1)?,
                content: row.get(2)?,
                last_modified_by: row.get(3)?,
                last_modified_at: row.get(4)?,
            })
        });

    match entry {
        Ok(entry) => HttpResponse::Ok().json(entry),
        Err(_) => HttpResponse::NotFound().finish(),
    }
}

async fn update_entry(
    data: web::Data<AppState>,
    entry_id: web::Path<String>,
    update_entry: web::Json<UpdateEntry>,
) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let now = Utc::now().to_rfc3339();
    let entry_id_str = entry_id.into_inner();

    let result = conn.execute(
        "UPDATE entries SET content = ?1, last_modified_by = ?2, last_modified_at = ?3 WHERE id = ?4",
        params![update_entry.content, update_entry.modified_by, now, entry_id_str],
    );

    match result {
        Ok(0) => HttpResponse::NotFound().finish(),
        Ok(_) => {
            conn.execute(
                "INSERT INTO edits (entry_id, content, last_modified_by, last_modified_at) VALUES (?1, ?2, ?3, ?4)",
                params![entry_id_str.clone(), update_entry.content, update_entry.modified_by, now],
            )
            .unwrap();

            HttpResponse::Ok().json(Entry {
                id: entry_id_str,
                title: String::new(),
                content: update_entry.content.clone(),
                last_modified_by: update_entry.modified_by.clone(),
                last_modified_at: now,
            })
        },
        Err(_) => HttpResponse::InternalServerError().finish(),
    }
}

async fn get_entry_edits(data: web::Data<AppState>, entry_id: web::Path<String>) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let mut stmt = conn.prepare("SELECT content, last_modified_by, last_modified_at FROM edits WHERE entry_id = ?1").unwrap();
    let edit_iter = stmt
        .query_map(params![entry_id.into_inner()], |row| {
            Ok(format!(
                "Content: {}, Modified By: {}, Modified At: {}",
                row.get::<_, String>(0)?,
                row.get::<_, String>(1)?,
                row.get::<_, String>(2)?
            ))
        })
        .unwrap();

    let mut edits = Vec::new();
    for edit in edit_iter {
        edits.push(edit.unwrap());
    }

    if edits.is_empty() {
        HttpResponse::NotFound().finish()
    } else {
        HttpResponse::Ok().json(edits)
    }
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
    )
    .unwrap();

    conn.execute(
        "CREATE TABLE IF NOT EXISTS edits (
            entry_id TEXT,
            content TEXT NOT NULL,
            last_modified_by TEXT NOT NULL,
            last_modified_at TEXT NOT NULL,
            FOREIGN KEY(entry_id) REFERENCES entries(id)
        )",
        [],
    )
    .unwrap();

    let data = web::Data::new(AppState {
        db: Mutex::new(conn),
    });

    HttpServer::new(move || {
        App::new()
            .app_data(data.clone())
            .route("/entries", web::get().to(get_entries))
            .route("/entries", web::post().to(create_entry))
            .route("/entries/{entryId}", web::get().to(get_entry))
            .route("/entries/{entryId}", web::put().to(update_entry))
            .route("/entries/{entryId}/edits", web::get().to(get_entry_edits))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}