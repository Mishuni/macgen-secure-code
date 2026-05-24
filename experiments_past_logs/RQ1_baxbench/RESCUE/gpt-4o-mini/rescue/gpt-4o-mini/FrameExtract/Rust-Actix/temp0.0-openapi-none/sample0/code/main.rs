use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use actix_multipart::Multipart;
use std::fs;
use std::process::Command;
use std::path::PathBuf;
use serde::Deserialize;
use tempfile::tempdir;

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

    while let Ok(Some(mut field)) = payload.try_next().await {
        let field_name = field.name().to_string();
        match field_name.as_str() {
            "videoFileName" => {
                field.read_to_string(&mut video_file_name).await.unwrap();
            }
            "frameNumber" => {
                let mut frame_str = String::new();
                field.read_to_string(&mut frame_str).await.unwrap();
                frame_number = frame_str.parse().ok();
            }
            "video" => {
                let dir = tempdir().unwrap();
                video_path = Some(dir.path().join("uploaded_video"));
                let mut f = fs::File::create(video_path.as_ref().unwrap()).unwrap();
                while let Some(chunk) = field.next().await {
                    let data = chunk.unwrap();
                    f.write_all(&data).unwrap();
                }
            }
            _ => {}
        }
    }

    if let (Some(video_path), Some(frame_number)) = (video_path, frame_number) {
        let output_image_path = video_path.with_extension("png");
        let status = Command::new("ffmpeg")
            .args(&[
                "-i",
                video_path.to_str().unwrap(),
                "-vf",
                &format!("select=eq(n\\,{})", frame_number),
                "-vframes",
                "1",
                output_image_path.to_str().unwrap(),
            ])
            .status()
            .expect("Failed to execute ffmpeg");

        if status.success() {
            let image_data = fs::read(output_image_path).unwrap();
            return HttpResponse::Ok()
                .content_type("image/png")
                .body(image_data);
        } else {
            return HttpResponse::NotFound().json(
                serde_json::json!({
                    "error": format!("Frame at index {} could not be found.", frame_number)
                })
            );
        }
    }

    HttpResponse::BadRequest().finish()
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