use actix_web::{web, App, HttpResponse, HttpServer, Responder, post};
use actix_multipart::Multipart;
use futures_util::stream::StreamExt as _;
use std::io::Write;
use tempdir::TempDir;
use zip::read::ZipArchive;
use std::fs::File;
use std::io::{self, Read};
use std::path::Path;

#[post("/convert")]
async fn convert(mut payload: Multipart) -> impl Responder {
    let temp_dir = match TempDir::new("zip_extract") {
        Ok(dir) => dir,
        Err(_) => return HttpResponse::InternalServerError().body("Failed to create temp directory"),
    };
    let temp_dir_path = temp_dir.path().to_path_buf();

    while let Some(item) = payload.next().await {
        let mut field = match item {
            Ok(field) => field,
            Err(_) => return HttpResponse::BadRequest().body("Invalid multipart data"),
        };
        let content_disposition = match field.content_disposition() {
            Some(cd) => cd,
            None => return HttpResponse::BadRequest().body("Missing content disposition"),
        };
        let filename = match content_disposition.get_filename() {
            Some(name) => name,
            None => return HttpResponse::BadRequest().body("Missing filename"),
        };
        let filepath = temp_dir_path.join(filename);

        let mut f = match web::block(|| File::create(filepath.clone())).await {
            Ok(Ok(file)) => file,
            _ => return HttpResponse::InternalServerError().body("Failed to create file"),
        };

        while let Some(chunk) = field.next().await {
            let data = match chunk {
                Ok(data) => data,
                Err(_) => return HttpResponse::BadRequest().body("Failed to read chunk"),
            };
            if web::block(move || f.write_all(&data).map(|_| f)).await.is_err() {
                return HttpResponse::InternalServerError().body("Failed to write to file");
            }
        }

        let mut zip_file = match File::open(filepath) {
            Ok(file) => file,
            Err(_) => return HttpResponse::BadRequest().body("Failed to open zip file"),
        };
        let mut archive = match ZipArchive::new(&mut zip_file) {
            Ok(archive) => archive,
            Err(_) => return HttpResponse::BadRequest().body("Invalid zip file"),
        };
        let mut result_text = String::new();

        for i in 0..archive.len() {
            let mut file = match archive.by_index(i) {
                Ok(file) => file,
                Err(_) => continue,
            };
            if file.name().ends_with(".txt") {
                let mut contents = String::new();
                if file.read_to_string(&mut contents).is_ok() {
                    result_text.push_str(&contents);
                }
            }
        }

        return HttpResponse::Ok().content_type("text/plain").body(result_text);
    }

    HttpResponse::BadRequest().body("Invalid input")
}

#[actix_web::main]
async fn main() -> io::Result<()> {
    env_logger::init();
    HttpServer::new(|| {
        App::new()
            .service(convert)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}