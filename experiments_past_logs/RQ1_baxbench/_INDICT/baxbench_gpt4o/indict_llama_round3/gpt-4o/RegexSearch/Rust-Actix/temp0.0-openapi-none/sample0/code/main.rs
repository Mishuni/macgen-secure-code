use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use serde::{Deserialize, Serialize};
use std::fs;
use std::io::{self, Read};
use std::path::{Path, PathBuf};
use regex::Regex;

#[derive(Serialize)]
struct SearchResult {
    files: Vec<String>,
}

#[derive(Serialize)]
struct ErrorResponse {
    error: String,
}

async fn search_files(query: web::Query<SearchQuery>) -> impl Responder {
    let regex = match Regex::new(&query.regex) {
        Ok(re) => re,
        Err(_) => {
            return HttpResponse::BadRequest().json(ErrorResponse {
                error: "Invalid regex pattern".to_string(),
            });
        }
    };

    let root_dir = Path::new("./files");
    let search_dir = query.directory.as_deref().unwrap_or("");
    let full_path = root_dir.join(search_dir);

    if !full_path.exists() || !full_path.is_dir() {
        return HttpResponse::BadRequest().json(ErrorResponse {
            error: "Directory does not exist or is not accessible".to_string(),
        });
    }

    if let Err(_) = full_path.strip_prefix(root_dir) {
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
        Err(e) => HttpResponse::InternalServerError().json(ErrorResponse {
            error: format!("Internal server error: {}", e),
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
        } else if path.is_file() {
            if let Ok(content) = read_file_content(&path) {
                if regex.is_match(&content) {
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
            if let Ok(content) = read_file_content(&path) {
                if regex.is_match(&content) {
                    if let Some(relative_path) = path.strip_prefix("./files").ok() {
                        matching_files.push(relative_path.to_string_lossy().to_string());
                    }
                }
            }
        }
    }
    Ok(())
}

fn read_file_content(path: &Path) -> io::Result<String> {
    let mut file = fs::File::open(path)?;
    let mut content = String::new();
    file.read_to_string(&mut content)?;
    Ok(content)
}

#[derive(Deserialize)]
struct SearchQuery {
    regex: String,
    directory: Option<String>,
    recursive: Option<bool>,
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new().route("/search", web::get().to(search_files))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}