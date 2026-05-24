use actix_web::{web, App, HttpServer, HttpResponse, Responder, middleware};
use actix_multipart::Multipart;
use futures_util::stream::StreamExt as _;
use std::io::Write;
use std::path::{Path, PathBuf};
use tempdir::TempDir;
use std::process::Command;
use serde::Deserialize;
use serde_json::json;

#[derive(Deserialize)]
struct GifParams {
    target_size: String,
    delay: Option<u32>,
    append_reverted: Option<bool>,
}

async fn create_gif(mut payload: Multipart) -> impl Responder {
    // Create a temporary directory for processing
    let temp_dir = match TempDir::new("gif_creator") {
        Ok(dir) => dir,
        Err(_) => return HttpResponse::InternalServerError().json(json!({"error": "Failed to create temporary directory"})),
    };

    let temp_dir_path = temp_dir.path();
    let mut image_paths = Vec::new();
    let mut params: Option<GifParams> = None;

    // Process multipart form data
    while let Some(Ok(mut field)) = payload.next().await {
        let content_disposition = field.content_disposition();
        let field_name = content_disposition.get_name().unwrap_or("");

        if field_name == "images" {
            // Save uploaded images to temporary files
            let file_name = uuid::Uuid::new_v4().to_string();
            let file_path = temp_dir_path.join(file_name);
            let mut file = match std::fs::File::create(&file_path) {
                Ok(f) => f,
                Err(_) => return HttpResponse::InternalServerError().json(json!({"error": "Failed to save uploaded file"})),
            };

            while let Some(Ok(chunk)) = field.next().await {
                if let Err(_) = file.write_all(&chunk) {
                    return HttpResponse::InternalServerError().json(json!({"error": "Failed to write to temporary file"}));
                }
            }

            image_paths.push(file_path);
        } else if field_name == "targetSize" || field_name == "delay" || field_name == "appendReverted" {
            // Collect parameters
            let mut data = Vec::new();
            while let Some(Ok(chunk)) = field.next().await {
                data.extend_from_slice(&chunk);
            }

            let value = String::from_utf8_lossy(&data).to_string();
            if field_name == "targetSize" {
                if params.is_none() {
                    params = Some(GifParams {
                        target_size: value,
                        delay: None,
                        append_reverted: None,
                    });
                } else {
                    params.as_mut().unwrap().target_size = value;
                }
            } else if field_name == "delay" {
                if let Ok(delay) = value.parse::<u32>() {
                    if params.is_none() {
                        params = Some(GifParams {
                            target_size: String::new(),
                            delay: Some(delay),
                            append_reverted: None,
                        });
                    } else {
                        params.as_mut().unwrap().delay = Some(delay);
                    }
                }
            } else if field_name == "appendReverted" {
                if let Ok(append_reverted) = value.parse::<bool>() {
                    if params.is_none() {
                        params = Some(GifParams {
                            target_size: String::new(),
                            delay: None,
                            append_reverted: Some(append_reverted),
                        });
                    } else {
                        params.as_mut().unwrap().append_reverted = Some(append_reverted);
                    }
                }
            }
        }
    }

    // Validate parameters
    let params = match params {
        Some(p) => p,
        None => return HttpResponse::BadRequest().json(json!({"error": "Missing required parameters"})),
    };

    if image_paths.is_empty() {
        return HttpResponse::BadRequest().json(json!({"error": "No images provided"}));
    }

    if !params.target_size.contains('x') || params.target_size.split('x').count() != 2 {
        return HttpResponse::BadRequest().json(json!({"error": "Invalid target size format"}));
    }

    let delay = params.delay.unwrap_or(10);
    let append_reverted = params.append_reverted.unwrap_or(false);

    // Prepare ImageMagick command
    let mut command = Command::new("convert");
    for image_path in &image_paths {
        command.arg(image_path);
    }

    if append_reverted {
        for image_path in image_paths.iter().rev() {
            command.arg(image_path);
        }
    }

    command.arg("-resize").arg(&params.target_size);
    command.arg("-delay").arg(delay.to_string());
    command.arg("-loop").arg("0");

    let output_gif_path = temp_dir_path.join("output.gif");
    command.arg(&output_gif_path);

    // Execute ImageMagick command
    match command.output() {
        Ok(output) => {
            if !output.status.success() {
                return HttpResponse::InternalServerError().json(json!({"error": "Failed to create GIF"}));
            }
        }
        Err(_) => return HttpResponse::InternalServerError().json(json!({"error": "Failed to execute ImageMagick command"})),
    }

    // Return the generated GIF
    match std::fs::read(&output_gif_path) {
        Ok(data) => HttpResponse::Ok()
            .content_type("image/gif")
            .body(data),
        Err(_) => HttpResponse::InternalServerError().json(json!({"error": "Failed to read generated GIF"})),
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();

    HttpServer::new(|| {
        App::new()
            .wrap(middleware::Logger::default())
            .route("/create-gif", web::post().to(create_gif))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}