use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};
use uuid::Uuid;

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

async fn get_entries() -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap_or_else(|_| {
        HttpResponse::InternalServerError().finish();
        std::process::exit(1);
    });
    
    let mut stmt = conn.prepare("SELECT id, title FROM entries").unwrap_or_else(|_| {
        HttpResponse::InternalServerError().finish();
        std::process::exit(1);
    });
    
    let entry_iter = stmt.query_map([], |row| {
        Ok(Entry {
            id: row.get(0)?,
            title: row.get(1)?,
            content: "".to_string(),
            last_modified_by: "".to_string(),
            last_modified_at: "".to_string(),
        })
    }).unwrap_or_else(|_| {
        HttpResponse::InternalServerError().finish();
        std::process::exit(1);
    });

    let mut entries = String::new();
    for entry in entry_iter {
        if let Ok(entry) = entry {
            entries.push_str(&format!("<a href=\"/entries/{}\">{}</a><br>", entry.id, entry.title));
        }
    }

    HttpResponse::Ok().content_type("text/html").body(entries)
}

async fn create_entry(new_entry: web::Json<NewEntry>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap_or_else(|_| {
        HttpResponse::InternalServerError().finish();
        std::process::exit(1);
    });
    
    let id = Uuid::new_v4().to_string();
    let now: DateTime<Utc> = Utc::now();
    
    if let Err(_) = conn.execute(
        "INSERT INTO entries (id, title, content, last_modified_by, last_modified_at) VALUES (?1, ?2, ?3, ?4, ?5)",
        params![id, new_entry.title, new_entry.content, new_entry.created_by, now.to_rfc3339()],
    ) {
        return HttpResponse::InternalServerError().finish();
    }

    let entry = Entry {
        id,
        title: new_entry.title.clone(),
        content: new_entry.content.clone(),
        last_modified_by: new_entry.created_by.clone(),
        last_modified_at: now.to_rfc3339(),
    };

    HttpResponse::Created().json(entry)
}

async fn get_entry(entry_id: web::Path<String>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap_or_else(|_| {
        HttpResponse::InternalServerError().finish();
        std::process::exit(1);
    });
    
    let mut stmt = conn.prepare("SELECT id, title, content, last_modified_by, last_modified_at FROM entries WHERE id = ?1").unwrap_or_else(|_| {
        HttpResponse::InternalServerError().finish();
        std::process::exit(1);
    });
    
    let entry_iter = stmt.query_map(params![entry_id.as_str()], |row| {
        Ok(Entry {
            id: row.get(0)?,
            title: row.get(1)?,
            content: row.get(2)?,
            last_modified_by: row.get(3)?,
            last_modified_at: row.get(4)?,
        })
    }).unwrap_or_else(|_| {
        HttpResponse::InternalServerError().finish();
        std::process::exit(1);
    });

    if let Some(entry) = entry_iter.into_iter().next() {
        if let Ok(entry) = entry {
            let response = format!("<h1>{}</h1><p>{}</p><p>Last modified by: {} at {}</p>",
                entry.title, entry.content, entry.last_modified_by, entry.last_modified_at);
            HttpResponse::Ok().content_type("text/html").body(response)
        } else {
            HttpResponse::NotFound().body("Entry not found")
        }
    } else {
        HttpResponse::NotFound().body("Entry not found")
    }
}

async fn update_entry(entry_id: web::Path<String>, update_entry: web::Json<UpdateEntry>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap_or_else(|_| {
        HttpResponse::InternalServerError().finish();
        std::process::exit(1);
    });
    
    let now: DateTime<Utc> = Utc::now();
    let result = conn.execute(
        "UPDATE entries SET content = ?1, last_modified_by = ?2, last_modified_at = ?3 WHERE id = ?4",
        params![update_entry.content, update_entry.modified_by, now.to_rfc3339(), entry_id.as_str()],
    );

    match result {
        Ok(0) => HttpResponse::NotFound().body("Entry not found"),
        Ok(_) => {
            let entry = Entry {
                id: entry_id.clone(),
                title: "".to_string(), // Title is not updated
                content: update_entry.content.clone(),
                last_modified_by: update_entry.modified_by.clone(),
                last_modified_at: now.to_rfc3339(),
            };
            HttpResponse::Ok().json(entry)
        },
        Err(_) => HttpResponse::InternalServerError().body("Error updating entry"),
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let conn = Connection::open("db.sqlite3").unwrap_or_else(|_| {
        HttpResponse::InternalServerError().finish();
        std::process::exit(1);
    });
    
    conn.execute(
        "CREATE TABLE IF NOT EXISTS entries (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            last_modified_by TEXT NOT NULL,
            last_modified_at TEXT NOT NULL
        )",
        [],
    ).unwrap_or_else(|_| {
        HttpResponse::InternalServerError().finish();
        std::process::exit(1);
    });

    HttpServer::new(|| {
        App::new()
            .route("/entries", web::get().to(get_entries))
            .route("/entries", web::post().to(create_entry))
            .route("/entries/{entryId}", web::get().to(get_entry))
            .route("/entries/{entryId}", web::put().to(update_entry))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}