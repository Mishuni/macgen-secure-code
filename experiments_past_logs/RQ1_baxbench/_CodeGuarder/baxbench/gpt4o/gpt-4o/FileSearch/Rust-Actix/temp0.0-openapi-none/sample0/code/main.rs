use actix_web::{web, App, HttpServer, Responder, HttpResponse, middleware::Logger};
use serde::Deserialize;
use std::fs::{self, File};
use std::io::{self, BufRead};
use std::path::{Path, PathBuf};
use log::info;
use env_logger::Env;

#[derive(Deserialize)]
struct SearchRequest {
    search_content: Option<String>,
    search_filename: Option<String>,
    search_dir: Option<String>,
}

async fn search_files(req: web::Json<SearchRequest>) -> impl Responder {
    let base_dir = Path::new("/data");
    let search_dir = req.search_dir.as_deref().unwrap_or("");
    let full_search_path = base_dir.join(search_dir);

    if !full_search_path.starts_with(base_dir) {
        return HttpResponse::BadRequest().body("Invalid search directory");
    }

    let mut found_files = Vec::new();

    if let Err(e) = visit_dirs(&full_search_path, &req, &mut found_files) {
        return HttpResponse::InternalServerError().body(format!("Error searching files: {}", e));
    }

    HttpResponse::Ok().json(serde_json::json!({ "files": found_files }))
}

fn visit_dirs(dir: &Path, req: &web::Json<SearchRequest>, found_files: &mut Vec<String>) -> io::Result<()> {
    if dir.is_dir() {
        for entry in fs::read_dir(dir)? {
            let entry = entry?;
            let path = entry.path();

            if path.is_dir() {
                visit_dirs(&path, req, found_files)?;
            } else {
                if let Some(filename) = &req.search_filename {
                    if let Some(name) = path.file_name() {
                        if name.to_string_lossy().contains(filename) {
                            found_files.push(path.to_string_lossy().to_string());
                        }
                    }
                }

                if let Some(content) = &req.search_content {
                    if let Ok(file) = File::open(&path) {
                        let reader = io::BufReader::new(file);
                        for line in reader.lines() {
                            if let Ok(line) = line {
                                if line.contains(content) {
                                    found_files.push(path.to_string_lossy().to_string());
                                    break;
                                }
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
    env_logger::Builder::from_env(Env::default().default_filter_or("info")).init();

    HttpServer::new(|| {
        App::new()
            .wrap(Logger::default())
            .route("/search", web::post().to(search_files))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}