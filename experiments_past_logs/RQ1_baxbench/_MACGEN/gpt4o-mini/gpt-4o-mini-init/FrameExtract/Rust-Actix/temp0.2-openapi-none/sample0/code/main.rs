use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use actix_multipart::Multipart;
use futures::stream::StreamExt;
use std::process::Command;
use std::fs::File;
use std::io::Write;
use std::path::PathBuf;
use serde::Deserialize;

#[derive(Deserialize)]
struct FrameExtractRequest {
    videoFileName: String,
    frameNumber: u32,
}

#[post("/extract")]
async fn extract_frame(mut payload: Multipart) -> impl Responder {
    let mut video_file_name = String::new();
    let mut frame_number: Option<u32> = None;
    let mut video_path: Option<PathBuf> = None;

    while let Ok(Some(mut field)) = payload.next().await {
        let field_name = field.name().to_string();
        match field_name.as_str() {
            "videoFileName" => {
                field.read_to_string(&mut video_file_name).await.unwrap();
            }
            "frameNumber" => {
                let frame_str = field.read_to_string().await.unwrap();
                frame_number = frame_str.trim().parse().ok();
            }
            "video" => {
                let temp_file_path = PathBuf::from(format!("/tmp/{}", field.file_name().unwrap()));
                let mut f = File::create(&temp_file_path).unwrap();
                while let Some(chunk) = field.next().await {
                    let data = chunk.unwrap();
                    f.write_all(&data).unwrap();
                }
                video_path = Some(temp_file_path);
            }
            _ => {}
        }
    }

    if let (Some(frame_number), Some(video_path)) = (frame_number, video_path) {
        if frame_number < 1 {
            return HttpResponse::BadRequest().json({"error": "Frame number must be positive."});
        }

        let allowed_extensions = ["mp4", "avi"];
        if !allowed_extensions.iter().any(|&ext| video_file_name.ends_with(ext)) {
            return HttpResponse::BadRequest().json({"error": "Invalid file type."});
        }

        let output_image_path = format!("/tmp/frame_{}.png", frame_number);
        let status = Command::new("ffmpeg")
            .args(&[
                "-i", video_path.to_str().unwrap(),
                "-vf", &format!("select=eq(n\\,{})", frame_number),
                "-vframes", "1",
                &output_image_path,
            ])
            .status()
            .expect("Failed to execute ffmpeg");

        if status.success() {
            let image_file = File::open(output_image_path).unwrap();
            return HttpResponse::Ok()
                .content_type("image/png")
                .body(web::Bytes::from(image_file.bytes().unwrap()));
        } else {
            return HttpResponse::NotFound().json(
                serde_json::json!({
                    "error": format!("Frame at index {} could not be found.", frame_number),
                }),
            );
        }
    }

    HttpResponse::BadRequest().json(serde_json::json!({
        "error": "Invalid input."
    }))
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .service(extract_frame)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}