use actix_web::{get, web, App, HttpResponse, HttpServer, Responder};
use regex::Regex;
use std::fs;
use std::path::{Path, PathBuf};

#[get("/search")]
async fn search_files(
    web::Query(params): web::Query<SearchParams>,
) -> impl Responder {
    let SearchParams { regex, directory, recursive } = params;

    // Set the root directory
    let root_dir = PathBuf::from("./files");
    let search_dir = match directory {
        Some(dir) => root_dir.join(sanitize_directory(&dir)),
        None => root_dir.clone(),
    };

    // Validate the directory
    if !search_dir.exists() || !search_dir.is_dir() {
        return HttpResponse::BadRequest().json(json!({"error": "Invalid directory."}));
    }

    // Compile the regex
    let regex = match Regex::new(&regex) {
        Ok(r) => r,
        Err(_) => return HttpResponse::BadRequest().json(json!({"error": "Malformed regex."})),
    };

    let mut matching_files = Vec::new();

    // Search files
    if let Err(e) = search_directory(&search_dir, &regex, recursive.unwrap_or(false), &mut matching_files) {
        return HttpResponse::InternalServerError().json(json!({"error": e.to_string()}));
    }

    HttpResponse::Ok().json(json!({"files": matching_files}))
}

fn search_directory(
    dir: &Path,
    regex: &Regex,
    recursive: bool,
    matching_files: &mut Vec<String>,
) -> std::io::Result<()> {
    for entry in fs::read_dir(dir)? {
        let entry = entry?;
        let path = entry.path();

        if path.is_dir() {
            if recursive {
                search_directory(&path, regex, recursive, matching_files)?;
            }
        } else if let Ok(content) = fs::read_to_string(&path) {
            if regex.is_match(&content) {
                if let Some(relative_path) = path.strip_prefix("./files").ok() {
                    matching_files.push(relative_path.to_string_lossy().to_string());
                }
            }
        }
    }
    Ok(())
}

fn sanitize_directory(directory: &str) -> String {
    // Prevent directory traversal by removing any path traversal sequences
    directory
        .replace("..", "")
        .replace("./", "")
        .replace("/", "")
}

#[derive(serde::Deserialize)]
struct SearchParams {
    regex: String,
    directory: Option<String>,
    recursive: Option<bool>,
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .service(search_files)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}