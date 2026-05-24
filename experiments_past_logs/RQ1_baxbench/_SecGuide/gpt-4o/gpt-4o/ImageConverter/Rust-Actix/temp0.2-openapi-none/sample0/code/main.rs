use actix_web::{web, App, HttpResponse, HttpServer, Responder, post};
use actix_multipart::Multipart;
use futures_util::stream::StreamExt as _;
use std::io::Write;
use std::process::Command;
use tempdir::TempDir;
use serde::Deserialize;
use std::path::Path;
use std::fs;
use log::error;
use sanitize_filename::sanitize;

#[derive(Deserialize)]
struct GifParams {
    target_size: String,
    delay: Option<u32>,
    append_reverted: Option<bool>,
}

#[post("/create-gif")]
async fn create_gif(mut payload: Multipart, params: web::Query<GifParams>) -> impl Responder {
    let temp_dir = match TempDir::new("gif_creator") {
        Ok(dir) => dir,
        Err(e) => {
            error!("Failed to create temporary directory: {}", e);
            return HttpResponse::InternalServerError().json(serde_json::json!({"error": "Internal server error"}));
        }
    };
    let mut image_paths = Vec::new();

    while let Some(item) = payload.next().await {
        let mut field = match item {
            Ok(f) => f,
            Err(e) => {
                error!("Failed to process multipart item: {}", e);
                return HttpResponse::BadRequest().json(serde_json::json!({"error": "Invalid multipart data"}));
            }
        };

        let content_disposition = match field.content_disposition() {
            Some(cd) => cd,
            None => {
                error!("Missing content disposition");
                return HttpResponse::BadRequest().json(serde_json::json!({"error": "Missing content disposition"}));
            }
        };

        let filename = match content_disposition.get_filename() {
            Some(name) => sanitize(name),
            None => {
                error!("Missing filename in content disposition");
                return HttpResponse::BadRequest().json(serde_json::json!({"error": "Missing filename"}));
            }
        };

        if filename.contains("..") {
            error!("Invalid filename containing path traversal sequences");
            return HttpResponse::BadRequest().json(serde_json::json!({"error": "Invalid filename"}));
        }

        let filepath = temp_dir.path().join(&filename);
        let mut f = match fs::File::create(&filepath) {
            Ok(file) => file,
            Err(e) => {
                error!("Failed to create file {}: {}", filepath.display(), e);
                return HttpResponse::InternalServerError().json(serde_json::json!({"error": "Internal server error"}));
            }
        };

        while let Some(chunk) = field.next().await {
            let data = match chunk {
                Ok(d) => d,
                Err(e) => {
                    error!("Failed to read chunk: {}", e);
                    return HttpResponse::InternalServerError().json(serde_json::json!({"error": "Internal server error"}));
                }
            };
            if let Err(e) = f.write_all(&data) {
                error!("Failed to write to file {}: {}", filepath.display(), e);
                return HttpResponse::InternalServerError().json(serde_json::json!({"error": "Internal server error"}));
            }
        }
        image_paths.push(filepath);
    }

    if image_paths.is_empty() {
        return HttpResponse::BadRequest().json(serde_json::json!({"error": "No images uploaded"}));
    }

    let delay = params.delay.unwrap_or(10);
    let append_reverted = params.append_reverted.unwrap_or(false);
    let target_size = &params.target_size;

    if !target_size.chars().all(|c| c.is_digit(10) || c == 'x') {
        return HttpResponse::BadRequest().json(serde_json::json!({"error": "Invalid target size"}));
    }

    let mut command = Command::new("convert");
    for path in &image_paths {
        command.arg(path);
    }

    if append_reverted {
        for path in image_paths.iter().rev() {
            command.arg(path);
        }
    }

    command.arg("-resize").arg(target_size);
    command.arg("-delay").arg(delay.to_string());
    command.arg("-loop").arg("0");
    let output_path = temp_dir.path().join("output.gif");
    command.arg(&output_path);

    let output = match command.output() {
        Ok(o) => o,
        Err(e) => {
            error!("Failed to execute command: {}", e);
            return HttpResponse::InternalServerError().json(serde_json::json!({"error": "Internal server error"}));
        }
    };

    if !output.status.success() {
        error!("Command execution failed: {:?}", output);
        return HttpResponse::InternalServerError().json(serde_json::json!({"error": "Failed to create GIF"}));
    }

    let gif_data = match fs::read(&output_path) {
        Ok(data) => data,
        Err(e) => {
            error!("Failed to read output GIF: {}", e);
            return HttpResponse::InternalServerError().json(serde_json::json!({"error": "Internal server error"}));
        }
    };

    HttpResponse::Ok().content_type("image/gif").body(gif_data)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    HttpServer::new(|| {
        App::new()
            .service(create_gif)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}