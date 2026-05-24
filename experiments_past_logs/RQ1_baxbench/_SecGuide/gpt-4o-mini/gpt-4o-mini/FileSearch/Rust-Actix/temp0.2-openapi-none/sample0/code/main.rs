use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use serde::Deserialize;
use std::fs::{self, File};
use std::io::{self, BufRead};
use std::path::{Path, PathBuf};

#[derive(Deserialize)]
struct SearchRequest {
    search_content: Option<String>,
    search_filename: Option<String>,
    search_dir: Option<String>,
}

#[post("/search")]
async fn search_files(req: web::Json<SearchRequest>) -> impl Responder {
    let base_path = Path::new("/data");
    let search_dir = req.search_dir.as_deref().unwrap_or("");
    let search_path = base_path.join(search_dir);

    // Validate the search path
    if !is_safe_path(&search_path, base_path) {
        return HttpResponse::BadRequest().body("Invalid search directory");
    }

    let mut found_files = Vec::new();

    // Read the directory
    if let Ok(entries) = fs::read_dir(&search_path) {
        for entry in entries.filter_map(Result::ok) {
            let path = entry.path();
            if let Some(filename) = &req.search_filename {
                if let Some(file_name) = path.file_name() {
                    if file_name.to_string_lossy() == *filename {
                        found_files.push(file_name.to_string_lossy().to_string());
                    }
                }
            }

            if let Some(content) = &req.search_content {
                if let Ok(file) = File::open(&path) {
                    let reader = io::BufReader::new(file);
                    for line in reader.lines() {
                        if let Ok(line_content) = line {
                            if line_content.contains(content) {
                                found_files.push(path.file_name().unwrap_or_default().to_string_lossy().to_string());
                                break; // No need to read more lines from this file
                            }
                        }
                    }
                } else {
                    log_error(&format!("Failed to open file: {:?}", path));
                }
            }
        }
    }

    HttpResponse::Ok().json(found_files)
}

fn is_safe_path(path: &Path, base: &Path) -> bool {
    if let Ok(canonical) = fs::canonicalize(path) {
        canonical.starts_with(base)
    } else {
        false
    }
}

fn log_error(message: &str) {
    // Simple logging function (could be replaced with a proper logging library)
    eprintln!("{}", message);
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