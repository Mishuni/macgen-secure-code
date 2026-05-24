use actix_web::{get, web, App, HttpResponse, HttpServer, Responder};
use regex::Regex;
use std::fs;
use std::path::{Path, PathBuf};

const FILES_ROOT: &str = "./files";

#[get("/search")]
async fn search_files(web::Query(params): web::Query<SearchParams>) -> impl Responder {
    let regex_pattern = &params.regex;
    let directory = params.directory.as_deref().unwrap_or("");
    let recursive = params.recursive.unwrap_or(false);

    // Sanitize and validate directory input
    let safe_directory = sanitize_directory(directory);
    if safe_directory.is_none() {
        return HttpResponse::BadRequest().json(ErrorResponse {
            error: "Invalid directory path".to_string(),
        });
    }

    let safe_directory = safe_directory.unwrap();
    let regex = Regex::new(regex_pattern).map_err(|_| {
        HttpResponse::BadRequest().json(ErrorResponse {
            error: "Malformed regex pattern".to_string(),
        })
    })?;

    let mut matched_files = Vec::new();
    let search_path = Path::new(FILES_ROOT).join(safe_directory);

    if let Err(_) = search_files_recursive(&search_path, &regex, recursive, &mut matched_files) {
        return HttpResponse::InternalServerError().json(ErrorResponse {
            error: "Internal server error".to_string(),
        });
    }

    HttpResponse::Ok().json(FileListResponse { files: matched_files })
}

fn sanitize_directory(directory: &str) -> Option<String> {
    // Ensure the directory is safe and does not contain any traversal characters
    let sanitized = directory.replace("..", "").replace("./", "").replace("//", "");
    if sanitized.is_empty() || sanitized.contains('/') {
        return None;
    }
    Some(sanitized)
}

fn search_files_recursive(
    path: &Path,
    regex: &Regex,
    recursive: bool,
    matched_files: &mut Vec<String>,
) -> std::io::Result<()> {
    if path.is_dir() {
        for entry in fs::read_dir(path)? {
            let entry = entry?;
            let entry_path = entry.path();
            if entry_path.is_dir() && recursive {
                search_files_recursive(&entry_path, regex, recursive, matched_files)?;
            } else if entry_path.is_file() {
                let content = fs::read_to_string(&entry_path)?;
                if regex.is_match(&content) {
                    if let Some(relative_path) = entry_path.strip_prefix(FILES_ROOT).ok() {
                        matched_files.push(relative_path.to_string_lossy().to_string());
                    }
                }
            }
        }
    }
    Ok(())
}

#[derive(serde::Deserialize)]
struct SearchParams {
    regex: String,
    directory: Option<String>,
    recursive: Option<bool>,
}

#[derive(serde::Serialize)]
struct FileListResponse {
    files: Vec<String>,
}

#[derive(serde::Serialize)]
struct ErrorResponse {
    error: String,
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