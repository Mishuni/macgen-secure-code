use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use actix_multipart::Multipart;
use futures::stream::StreamExt;
use std::fs;
use std::process::Command;
use std::path::PathBuf;
use serde::Deserialize;

#[derive(Deserialize)]
struct GifRequest {
    targetSize: String,
    delay: Option<u32>,
    appendReverted: Option<bool>,
}

async fn create_gif(mut payload: Multipart) -> impl Responder {
    let mut images: Vec<PathBuf> = Vec::new();
    let mut target_size: Option<String> = None;
    let mut delay: Option<u32> = None;
    let mut append_reverted: Option<bool> = None;

    while let Some(item) = payload.next().await {
        let mut field = item.unwrap();
        let content_disposition = field.content_disposition().unwrap();
        let name = content_disposition.get_name().unwrap();

        match name {
            "images" => {
                let filename = format!("temp_{}", uuid::Uuid::new_v4());
                let filepath = PathBuf::from(format!("/tmp/{}", filename));
                let mut f = fs::File::create(&filepath).unwrap();
                while let Some(chunk) = field.next().await {
                    let data = chunk.unwrap();
                    f.write_all(&data).unwrap();
                }
                images.push(filepath);
            }
            "targetSize" => {
                target_size = Some(field.next().await.unwrap().unwrap().to_string());
            }
            "delay" => {
                delay = Some(field.next().await.unwrap().unwrap().parse().unwrap());
            }
            "appendReverted" => {
                append_reverted = Some(field.next().await.unwrap().unwrap().parse().unwrap());
            }
            _ => {}
        }
    }

    if images.is_empty() || target_size.is_none() {
        return HttpResponse::BadRequest().json("Images and target size are required.");
    }

    let target_size = target_size.unwrap();
    let delay = delay.unwrap_or(10);
    let append_reverted = append_reverted.unwrap_or(false);

    let mut convert_command = Command::new("convert");
    convert_command.args(&images);
    convert_command.arg("-delay").arg(delay.to_string());
    convert_command.arg("-resize").arg(target_size);
    convert_command.arg("output.gif");

    if append_reverted {
        convert_command.arg("output.gif").arg("-reverse");
    }

    let output = convert_command.output().expect("Failed to execute command");

    if !output.status.success() {
        return HttpResponse::InternalServerError().json("Failed to create GIF.");
    }

    HttpResponse::Ok()
        .content_type("image/gif")
        .body(fs::read("output.gif").unwrap())
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .route("/create-gif", web::post().to(create_gif))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}