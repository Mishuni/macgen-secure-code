use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use serde::Serialize;
use std::fs;
use std::io::{self, BufRead};
use std::path::{Path, PathBuf};
use regex::RegexBuilder;

#[derive(Serialize)]
struct SearchResult {
    files: Vec<String>,
}

#[derive(Serialize)]
struct ErrorResponse {
    error: String,
}

async fn search_files(
    query: web::Query<std::collections::HashMap<String, String>>,
) -> impl Responder {
    let regex_pattern = match query.get("regex") {
        Some(pattern) => pattern,
        None => {
            return HttpResponse::BadRequest().json(ErrorResponse {
                error: "Missing regex parameter".to_string(),
            });
        }
    };

    let directory = query.get("directory").unwrap_or(&".".to_string());
    let recursive = query
        .get("recursive")
        .map(|r| r == "true")
        .unwrap_or(false);

    // Canonicalize the directory path to prevent directory traversal
    let root_dir = match fs::canonicalize("./files") {
        Ok(path) => path,
        Err(_) => {
            return HttpResponse::InternalServerError().json(ErrorResponse {
                error: "Failed to access root directory".to_string(),
            });
        }
    };

    let target_dir = match fs::canonicalize(root_dir.join(directory)) {
        Ok(path) => path,
        Err(_) => {
            return HttpResponse::BadRequest().json(ErrorResponse {
                error: "Invalid directory path".to_string(),
            });
        }
    };

    // Ensure the target directory is within the root directory
    if !target_dir.starts_with(&root_dir) {
        return HttpResponse::BadRequest().json(ErrorResponse {
            error: "Directory traversal attempt detected".to_string(),
        });
    }

    // Compile the regex pattern with a timeout to prevent ReDoS
    let regex = match RegexBuilder::new(regex_pattern)
        .size_limit(1_000_000) // Limit the size of the regex
        .build()
    {
        Ok(re) => re,
        Err(_) => {
            return HttpResponse::BadRequest().json(ErrorResponse {
                error: "Invalid regex pattern".to_string(),
            });
        }
    };

    let mut matching_files = Vec::new();

    // Search files
    if let Err(_) = search_in_directory(&target_dir, &regex, recursive, &mut matching_files) {
        return HttpResponse::InternalServerError().json(ErrorResponse {
            error: "Error searching files".to_string(),
        });
    }

    HttpResponse::Ok().json(SearchResult {
        files: matching_files,
    })
}

fn search_in_directory(
    dir: &Path,
    regex: &Regex,
    recursive: bool,
    matching_files: &mut Vec<String>,
) -> io::Result<()> {
    if dir.is_dir() {
        for entry in fs::read_dir(dir)? {
            let entry = entry?;
            let path = entry.path();

            if path.is_dir() && recursive {
                search_in_directory(&path, regex, recursive, matching_files)?;
            } else if path.is_file() {
                if let Ok(file) = fs::File::open(&path) {
                    let reader = io::BufReader::new(file);
                    for line in reader.lines() {
                        if let Ok(content) = line {
                            if regex.is_match(&content) {
                                if let Some(relative_path) = path.strip_prefix("./files").ok() {
                                    matching_files.push(relative_path.to_string_lossy().to_string());
                                }
                                break;
                            }
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