use actix_multipart::Multipart;
use actix_web::{web, App, HttpResponse, HttpServer, Responder, post};
use futures_util::stream::StreamExt as _;
use std::fs::File;
use std::io::Write;
use std::process::Command;
use tempdir::TempDir;
use serde::Deserialize;
use serde_json::json;

#[derive(Deserialize)]
struct FormData {
    videoFileName: String,
    frameNumber: u32,
}

#[post("/extract")]
async fn extract(mut payload: Multipart) -> impl Responder {
    let temp_dir = match TempDir::new("video_frames") {
        Ok(dir) => dir,
        Err(_) => return HttpResponse::InternalServerError().json(json!({"error": "Failed to create temp dir"})),
    };
    let mut video_path = None;
    let mut frame_number = None;

    while let Some(item) = payload.next().await {
        let mut field = match item {
            Ok(field) => field,
            Err(_) => return HttpResponse::BadRequest().json(json!({"error": "Invalid form data"})),
        };
        let content_disposition = match field.content_disposition() {
            Some(cd) => cd,
            None => return HttpResponse::BadRequest().json(json!({"error": "Missing content disposition"})),
        };
        let name = match content_disposition.get_name() {
            Some(name) => name,
            None => return HttpResponse::BadRequest().json(json!({"error": "Missing field name"})),
        };

        if name == "video" {
            let file_path = temp_dir.path().join("uploaded_video.mp4");
            let mut f = match File::create(&file_path) {
                Ok(file) => file,
                Err(_) => return HttpResponse::InternalServerError().json(json!({"error": "Failed to create file"})),
            };
            while let Some(chunk) = field.next().await {
                let data = match chunk {
                    Ok(data) => data,
                    Err(_) => return HttpResponse::BadRequest().json(json!({"error": "Failed to read chunk"})),
                };
                if f.write_all(&data).is_err() {
                    return HttpResponse::InternalServerError().json(json!({"error": "Failed to write to file"}));
                }
            }
            video_path = Some(file_path);
        } else if name == "frameNumber" {
            let mut data = Vec::new();
            while let Some(chunk) = field.next().await {
                let chunk_data = match chunk {
                    Ok(data) => data,
                    Err(_) => return HttpResponse::BadRequest().json(json!({"error": "Failed to read chunk"})),
                };
                data.extend_from_slice(&chunk_data);
            }
            frame_number = match String::from_utf8(data).ok().and_then(|s| s.parse::<u32>().ok()) {
                Some(num) => Some(num),
                None => return HttpResponse::BadRequest().json(json!({"error": "Invalid frame number"})),
            };
        }
    }

    if let (Some(video_path), Some(frame_number)) = (video_path, frame_number) {
        let output_image_path = temp_dir.path().join("frame.png");
        let ffmpeg_status = Command::new("ffmpeg")
            .args(&[
                "-i",
                video_path.to_str().unwrap(),
                "-vf",
                &format!("select=eq(n\\,{})", frame_number),
                "-vframes",
                "1",
                output_image_path.to_str().unwrap(),
            ])
            .status();

        match ffmpeg_status {
            Ok(status) if status.success() && output_image_path.exists() => {
                match std::fs::read(&output_image_path) {
                    Ok(image_data) => HttpResponse::Ok().content_type("image/png").body(image_data),
                    Err(_) => HttpResponse::InternalServerError().json(json!({"error": "Failed to read output image"})),
                }
            }
            _ => HttpResponse::NotFound().json(json!({
                "error": format!("Frame at index {} could not be found.", frame_number)
            })),
        }
    } else {
        HttpResponse::BadRequest().json(json!({"error": "Missing video or frame number"}))
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    HttpServer::new(|| {
        App::new()
            .service(extract)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}