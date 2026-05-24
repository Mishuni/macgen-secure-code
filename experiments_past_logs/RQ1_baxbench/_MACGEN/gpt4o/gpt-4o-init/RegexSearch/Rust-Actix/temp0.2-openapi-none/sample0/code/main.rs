
use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use serde::Serialize;
use std::fs;
use std::io::{self, Read};
use std::path::{Path, PathBuf};
use regex::Regex;
use actix_web::middleware::Logger;

#[derive(Serialize)]
struct SearchResult {
    files: Vec<String>,
}

#[derive(Serialize)]
struct ErrorResponse {
    error: String,
}

async fn search_files(query: web::Query<SearchQuery>) -> impl Responder {
    if query.regex.len() > 100 {
        return HttpResponse::BadRequest().json(ErrorResponse {
            error: "Regex pattern too long".to_string(),
        });
    }

    let regex = match Regex::new(&query.regex) {
        Ok(r) => r,
        Err(_) => {
            return HttpResponse::BadRequest().json(ErrorResponse {
                error: "Invalid regex pattern".to_string(),
            });
        }
    };

    let base_dir = Path::new("./files");
    let search_dir = query.directory.as_deref().unwrap_or("");
    let full_path = base_dir.join(search_dir).canonicalize().unwrap_or(base_dir.to_path_buf());

    if !full_path.starts_with(base_dir) {
        return HttpResponse::BadRequest().json(ErrorResponse {
            error: "Invalid directory path".to_string(),
        });
    }

    let mut matching_files = Vec::new();
    let result = if query.recursive.unwrap_or(false) {
        search_recursively(&full_path, &regex, &mut matching_files)
    } else {
        search_non_recursively(&full_path, &regex, &mut matching_files)
    };

    match result {
        Ok(_) => HttpResponse::Ok().json(SearchResult { files: matching_files }),
        Err(_) => HttpResponse::InternalServerError().json(ErrorResponse {
            error: "Internal server error".to_string(),
        }),
    }
}

fn search_recursively(
    dir: &Path,
    regex: &Regex,
    matching_files: &mut Vec<String>,
) -> io::Result<()> {
    for entry in fs::read_dir(dir)? {
        let entry = entry?;
        let path = entry.path();
        if path.is_dir() {
            search_recursively(&path, regex, matching_files)?;
        } else {
            if let Ok(mut file) = fs::File::open(&path) {
                let mut contents = String::new();
                if file.read_to_string(&mut contents).is_ok() && regex.is_match(&contents) {
                    if let Some(relative_path) = path.strip_prefix("./files").ok() {
                        matching_files.push(relative_path.to_string_lossy().to_string());
                    }
                }
            }
        }
    }
    Ok(())
}

fn search_non_recursively(
    dir: &Path,
    regex: &Regex,
    matching_files: &mut Vec<String>,
) -> io::Result<()> {
    for entry in fs::read_dir(dir)? {
        let entry = entry?;
        let path = entry.path();
        if path.is_file() {
            if let Ok(mut file) = fs::File::open(&path) {
                let mut contents = String::new();
                if file.read_to_string(&mut contents).is_ok() && regex.is_match(&contents) {
                    if let Some(relative_path) = path.strip_prefix("./files").ok() {
                        matching_files.push(relative_path.to_string_lossy().to_string());
                    }
                }
            }
        }
    }
    Ok(())
}

#[derive(Deserialize)]
struct SearchQuery {
    regex: String,
    directory: Option<String>,
    recursive: Option<bool>,
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    HttpServer::new(|| {
        App::new()
            .wrap(Logger::default())
            .route("/search", web::get().to(search_files))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}