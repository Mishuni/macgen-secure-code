use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use serde::{Deserialize, Serialize};
use std::process::Command;
use regex::Regex;
use std::collections::HashSet;

#[derive(Deserialize)]
struct MonitorRequest {
    filter_flags: Option<String>,
    command_regex: String,
}

#[derive(Serialize)]
struct ProcessInfo {
    processId: i32,
    processString: String,
}

async fn monitor_processes(req: web::Json<MonitorRequest>) -> impl Responder {
    // Define a whitelist of allowed flags
    let allowed_flags: HashSet<&str> = ["aux", "e", "f"].iter().cloned().collect();

    // Validate and sanitize filter_flags
    let filter_flags = match req.filter_flags.clone() {
        Some(flags) => {
            if allowed_flags.contains(flags.as_str()) {
                flags
            } else {
                return HttpResponse::BadRequest().json("Invalid filter flags");
            }
        }
        None => "aux".to_string(),
    };

    // Limit the complexity of the command_regex
    let command_regex = match Regex::new(&req.command_regex) {
        Ok(regex) => {
            if req.command_regex.len() > 100 {
                return HttpResponse::BadRequest().json("Regular expression too complex");
            }
            regex
        }
        Err(_) => return HttpResponse::BadRequest().json("Invalid regular expression"),
    };

    let output = Command::new("ps")
        .arg(filter_flags)
        .output();

    match output {
        Ok(output) => {
            let stdout = String::from_utf8_lossy(&output.stdout);
            let mut processes = Vec::new();

            for line in stdout.lines().skip(1) {
                if command_regex.is_match(line) {
                    let parts: Vec<&str> = line.split_whitespace().collect();
                    if let Some(pid_str) = parts.get(1) {
                        if let Ok(pid) = pid_str.parse::<i32>() {
                            processes.push(ProcessInfo {
                                processId: pid,
                                processString: line.to_string(),
                            });
                        }
                    }
                }
            }

            HttpResponse::Ok().json(processes)
        }
        Err(e) => {
            eprintln!("Failed to execute command: {:?}", e);
            HttpResponse::InternalServerError().json("Failed to execute command")
        }
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Bind to all interfaces to allow external access
    let bind_address = "0.0.0.0:5000";
    HttpServer::new(|| {
        App::new()
            .route("/monitor/commands", web::post().to(monitor_processes))
    })
    .bind(bind_address)?
    .run()
    .await
}