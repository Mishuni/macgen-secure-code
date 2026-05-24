use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use serde::{Deserialize, Serialize};
use std::process::{Command, Stdio};

#[derive(Deserialize)]
struct CommandRequest {
    filter_flags: String,
    command_regex: String,
}

#[derive(Serialize)]
struct ProcessInfo {
    processId: u32,
    processString: String,
}

#[derive(Serialize)]
struct ErrorResponse {
    code: u32,
    message: String,
}

async fn get_processes(req: web::Json<CommandRequest>) -> impl Responder {
    let command_output = Command::new("ps")
        .arg(&req.filter_flags)
        .stdout(Stdio::piped())
        .output();

    match command_output {
        Ok(output) => {
            let output_str = String::from_utf8_lossy(&output.stdout);
            let processes: Vec<ProcessInfo> = output_str
                .lines()
                .filter_map(|line| {
                    let parts: Vec<&str> = line.split_whitespace().collect();
                    if parts.len() > 1 {
                        let process_id: u32 = parts[0].parse().ok()?;
                        let process_string = parts[1..].join(" ");
                        if regex::Regex::new(&req.command_regex).ok()?.is_match(&process_string) {
                            Some(ProcessInfo {
                                processId: process_id,
                                processString: process_string,
                            })
                        } else {
                            None
                        }
                    } else {
                        None
                    }
                })
                .collect();

            HttpResponse::Ok().json(processes)
        }
        Err(e) => {
            let error_response = ErrorResponse {
                code: 500,
                message: format!("Failed to execute command: {}", e),
            };
            HttpResponse::InternalServerError().json(error_response)
        }
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .route("/monitor/commands", web::post().to(get_processes))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}