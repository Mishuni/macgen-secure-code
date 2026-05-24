use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use serde::{Deserialize, Serialize};
use std::fs::{self, File};
use std::io::{self, Read};
use std::path::{Path, PathBuf};

#[derive(Deserialize)]
struct SearchRequest {
    search_content: Option<String>,
    search_filename: Option<String>,
    search_dir: Option<String>,
}

#[derive(Serialize)]
struct SearchResponse {
    files: Vec<String>,
}

fn sanitize_path(base: &Path, search_dir: &str) -> Option<PathBuf> {
    let sanitized_path = base.join(search_dir);
    if sanitized_path.starts_with(base) {
        Some(sanitized_path)
    } else {
        None
    }
}

fn matches_search_criteria(filename: &str, content: &str, search_filename: &Option<String>, search_content: &Option<String>) -> bool {
    let matches_filename = search_filename.as_ref().map_or(true, |name| filename.contains(name));
    let matches_content = search_content.as_ref().map_or(true, |search_content| content.contains(search_content));
    matches_filename || matches_content
}

#[post("/search")]
async fn search_files(req: web::Json<SearchRequest>) -> impl Responder {
    let base_path = PathBuf::from("/data");
    let mut found_files = Vec::new();

    if let Some(search_dir) = &req.search_dir {
        if let Some(search_path) = sanitize_path(&base_path, search_dir) {
            if let Ok(entries) = fs::read_dir(&search_path) {
                for entry in entries.filter_map(Result::ok) {
                    let path = entry.path();
                    if path.is_file() {
                        let filename = path.file_name().unwrap().to_string_lossy().to_string();
                        let mut content = String::new();
                        if let Ok(mut file) = File::open(&path) {
                            if file.read_to_string(&mut content).is_ok() {
                                if matches_search_criteria(&filename, &content, &req.search_filename, &req.search_content) {
                                    found_files.push(path.to_string_lossy().to_string());
                                }
                            }
                        }
                    }
                }
            }
        } else {
            return HttpResponse::BadRequest().finish();
        }
    }

    HttpResponse::Ok().json(SearchResponse { files: found_files })
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