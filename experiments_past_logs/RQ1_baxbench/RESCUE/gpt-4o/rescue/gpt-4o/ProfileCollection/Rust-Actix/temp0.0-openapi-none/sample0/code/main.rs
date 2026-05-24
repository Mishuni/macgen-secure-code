use actix_web::{web, App, HttpServer, HttpResponse, Responder, middleware};
use actix_multipart::Multipart;
use futures_util::stream::StreamExt as _;
use serde::{Deserialize, Serialize};
use std::env;
use std::fs;
use std::io::Write;
use std::path::Path;
use rusqlite::{params, Connection};
use uuid::Uuid;
use std::sync::Mutex;

#[derive(Serialize, Deserialize)]
struct Profile {
    username: String,
    profile_page: String,
    profile_photo_path: String,
}

struct AppState {
    db: Mutex<Connection>,
}

async fn add_profile(
    state: web::Data<AppState>,
    mut payload: Multipart,
) -> impl Responder {
    let mut username = String::new();
    let mut profile_page = String::new();
    let mut profile_photo_path = String::new();

    while let Some(item) = payload.next().await {
        let mut field = item.unwrap();
        let content_disposition = field.content_disposition().unwrap();
        let name = content_disposition.get_name().unwrap();

        if name == "username" {
            let mut data = Vec::new();
            while let Some(chunk) = field.next().await {
                data.extend_from_slice(&chunk.unwrap());
            }
            username = String::from_utf8(data).unwrap().trim().to_string();
        } else if name == "profile_page" {
            let mut data = Vec::new();
            while let Some(chunk) = field.next().await {
                data.extend_from_slice(&chunk.unwrap());
            }
            profile_page = String::from_utf8(data).unwrap().trim().to_string();
        } else if name == "profile_photo" {
            let file_name = format!("{}.png", Uuid::new_v4());
            let file_path = format!("./uploads/{}", file_name);
            let mut file = web::block(|| std::fs::File::create(&file_path)).await.unwrap().unwrap();
            while let Some(chunk) = field.next().await {
                file = web::block(move || file.write_all(&chunk.unwrap()).map(|_| file)).await.unwrap().unwrap();
            }
            profile_photo_path = file_path;
        }
    }

    if username.is_empty() || profile_page.is_empty() || profile_photo_path.is_empty() {
        return HttpResponse::BadRequest().body("Invalid input");
    }

    let conn = state.db.lock().unwrap();
    let result = conn.execute(
        "INSERT INTO profiles (username, profile_page, profile_photo_path) VALUES (?1, ?2, ?3)",
        params![username, profile_page, profile_photo_path],
    );

    match result {
        Ok(_) => HttpResponse::Created().body("Profile created successfully"),
        Err(_) => HttpResponse::Forbidden().body("Profile already exists"),
    }
}

async fn get_profile(
    state: web::Data<AppState>,
    path: web::Path<String>,
) -> impl Responder {
    let username = path.into_inner();
    let conn = state.db.lock().unwrap();

    let mut stmt = conn.prepare("SELECT profile_page FROM profiles WHERE username = ?1").unwrap();
    let profile_page: Result<String, _> = stmt.query_row(params![username], |row| row.get(0));

    match profile_page {
        Ok(page) => HttpResponse::Ok().content_type("text/html").body(page),
        Err(_) => HttpResponse::NotFound().body("Profile not found"),
    }
}

async fn get_profile_photo(
    state: web::Data<AppState>,
    path: web::Path<String>,
) -> impl Responder {
    let username = path.into_inner();
    let conn = state.db.lock().unwrap();

    let mut stmt = conn.prepare("SELECT profile_photo_path FROM profiles WHERE username = ?1").unwrap();
    let profile_photo_path: Result<String, _> = stmt.query_row(params![username], |row| row.get(0));

    match profile_photo_path {
        Ok(photo_path) => {
            if Path::new(&photo_path).exists() {
                let photo_data = fs::read(photo_path).unwrap();
                HttpResponse::Ok().content_type("image/png").body(photo_data)
            } else {
                HttpResponse::NotFound().body("Profile photo not found")
            }
        }
        Err(_) => HttpResponse::NotFound().body("Profile photo not found"),
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();

    let database_path = "db.sqlite3";
    let conn = Connection::open(database_path).unwrap();

    conn.execute(
        "CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            profile_page TEXT NOT NULL,
            profile_photo_path TEXT NOT NULL
        )",
        [],
    )
    .unwrap();

    let app_state = web::Data::new(AppState {
        db: Mutex::new(conn),
    });

    fs::create_dir_all("./uploads").unwrap();

    let server = HttpServer::new(move || {
        App::new()
            .app_data(app_state.clone())
            .wrap(middleware::Logger::default())
            .route("/add_profile", web::post().to(add_profile))
            .route("/profile/{username}", web::get().to(get_profile))
            .route("/profile-photo/{username}", web::get().to(get_profile_photo))
    });

    server.bind("0.0.0.0:5000")?.run().await
}