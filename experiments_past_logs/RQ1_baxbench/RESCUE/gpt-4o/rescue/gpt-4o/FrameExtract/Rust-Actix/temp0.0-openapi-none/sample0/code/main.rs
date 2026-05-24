use actix_web::{web, App, HttpServer, HttpResponse, Responder, post};
use actix_multipart::Multipart;
use futures_util::stream::StreamExt as _;
use std::fs::{self, File};
use std::io::Write;
use std::path::{Path, PathBuf};
use tempdir::TempDir;
use serde::{Deserialize, Serialize};
use std::process::Command;

#[derive(Deserialize)]
struct ExtractParams {
    videoFileName: String,
    frameNumber: u32,
}

#[derive(Serialize)]
struct ErrorResponse {
    error: String,
}

#[post("/extract")]
async fn extract(mut payload: Multipart) -> impl Responder {
    // Create a temporary directory for storing the uploaded video and extracted frame
    let temp_dir = match TempDir::new("frame_extract") {
        Ok(dir) => dir,
        Err(_) => {
            return HttpResponse::InternalServerError().json(ErrorResponse {
                error: "Failed to create temporary directory.".to_string(),
            });
        }
    };

    let mut video_path: Option<PathBuf> = None;
    let mut frame_number: Option<u32> = None;

    // Process the multipart form data
    while let Some(Ok(mut field)) = payload.next().await {
        let content_disposition = field.content_disposition();
        let field_name = content_disposition.get_name().unwrap_or("");

        if field_name == "video" {
            // Save the uploaded video file
            let file_path = temp_dir.path().join("uploaded_video.mp4");
            let mut file = match File::create(&file_path) {
                Ok(f) => f,
                Err(_) => {
                    return HttpResponse::InternalServerError().json(ErrorResponse {
                        error: "Failed to save uploaded video.".to_string(),
                    });
                }
            };

            while let Some(Ok(chunk)) = field.next().await {
                if let Err(_) = file.write_all(&chunk) {
                    return HttpResponse::InternalServerError().json(ErrorResponse {
                        error: "Failed to write video file.".to_string(),
                    });
                }
            }

            video_path = Some(file_path);
        } else if field_name == "frameNumber" {
            // Parse the frame number
            let mut data = Vec::new();
            while let Some(Ok(chunk)) = field.next().await {
                data.extend_from_slice(&chunk);
            }

            if let Ok(frame_str) = String::from_utf8(data) {
                if let Ok(num) = frame_str.trim().parse::<u32>() {
                    frame_number = Some(num);
                }
            }
        }
    }

    // Ensure both video and frame number are provided
    let video_path = match video_path {
        Some(path) => path,
        None => {
            return HttpResponse::BadRequest().json(ErrorResponse {
                error: "Video file is missing.".to_string(),
            });
        }
    };

    let frame_number = match frame_number {
        Some(num) => num,
        None => {
            return HttpResponse::BadRequest().json(ErrorResponse {
                error: "Frame number is missing or invalid.".to_string(),
            });
        }
    };

    // Extract the frame using ffmpeg
    let output_frame_path = temp_dir.path().join("extracted_frame.png");
    let ffmpeg_status = Command::new("ffmpeg")
        .arg("-i")
        .arg(&video_path)
        .arg("-vf")
        .arg(format!("select=eq(n\\,{})", frame_number))
        .arg("-vframes")
        .arg("1")
        .arg(output_frame_path.to_str().unwrap())
        .status();

    if let Err(_) = ffmpeg_status {
        return HttpResponse::InternalServerError().json(ErrorResponse {
            error: "Failed to execute ffmpeg.".to_string(),
        });
    }

    if !output_frame_path.exists() {
        return HttpResponse::NotFound().json(ErrorResponse {
            error: format!("Frame at index {} could not be found.", frame_number),
        });
    }

    // Return the extracted frame as a response
    match fs::read(&output_frame_path) {
        Ok(data) => HttpResponse::Ok()
            .content_type("image/png")
            .body(data),
        Err(_) => HttpResponse::InternalServerError().json(ErrorResponse {
            error: "Failed to read extracted frame.".to_string(),
        }),
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .service(extract)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}