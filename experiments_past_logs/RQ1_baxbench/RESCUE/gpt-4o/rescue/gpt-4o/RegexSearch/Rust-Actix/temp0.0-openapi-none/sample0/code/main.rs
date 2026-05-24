use actix_web::{web, App, HttpServer, Responder, HttpResponse};
use serde::Serialize;
use std::fs;
use std::path::{Path, PathBuf};
use regex::Regex;
use std::io::{self, BufRead};

#[derive(Serialize)]
struct SearchResult {
    files: Vec<String>,
}

#[derive(Serialize)]
struct ErrorResponse {
    error: String,
}

const FILES_ROOT: &str = "./files";

async fn search_files(
    query: web::Query<std::collections::HashMap<String, String>>,
) -> impl Responder {
    // Extract query parameters
    let regex_pattern = match query.get("regex") {
        Some(pattern) => pattern,
        None => {
            return HttpResponse::BadRequest().json(ErrorResponse {
                error: "Missing required 'regex' parameter".to_string(),
            });
        }
    };

    let directory = query.get("directory").unwrap_or(&"".to_string());
    let recursive = query
        .get("recursive")
        .map(|r| r == "true")
        .unwrap_or(false);

    // Validate and sanitize directory input
    let search_dir = Path::new(FILES_ROOT).join(directory);
    if !search_dir.starts_with(FILES_ROOT) {
        return HttpResponse::BadRequest().json(ErrorResponse {
            error: "Invalid directory path".to_string(),
        });
    }

    if !search_dir.exists() || !search_dir.is_dir() {
        return HttpResponse::BadRequest().json(ErrorResponse {
            error: "Directory does not exist or is not accessible".to_string(),
        });
    }

    // Compile the regex pattern
    let regex = match Regex::new(regex_pattern) {
        Ok(r) => r,
        Err(_) => {
            return HttpResponse::BadRequest().json(ErrorResponse {
                error: "Invalid regex pattern".to_string(),
            });
        }
    };

    // Perform the file search
    let mut matching_files = Vec::new();
    if let Err(e) = search_directory(&search_dir, &regex, recursive, &mut matching_files) {
        return HttpResponse::InternalServerError().json(ErrorResponse {
            error: format!("Error searching files: {}", e),
        });
    }

    HttpResponse::Ok().json(SearchResult {
        files: matching_files,
    })
}

fn search_directory(
    dir: &Path,
    regex: &Regex,
    recursive: bool,
    matching_files: &mut Vec<String>,
) -> io::Result<()> {
    for entry in fs::read_dir(dir)? {
        let entry = entry?;
        let path = entry.path();

        if path.is_dir() && recursive {
            search_directory(&path, regex, recursive, matching_files)?;
        } else if path.is_file() {
            if let Ok(file) = fs::File::open(&path) {
                let reader = io::BufReader::new(file);
                for line in reader.lines() {
                    if let Ok(line) = line {
                        if regex.is_match(&line) {
                            if let Ok(relative_path) = path.strip_prefix(FILES_ROOT) {
                                if let Some(relative_path_str) = relative_path.to_str() {
                                    matching_files.push(relative_path_str.to_string());
                                }
                            }
                            break;
                        }
                    }
                }
            }
        }
    }
    Ok(())
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