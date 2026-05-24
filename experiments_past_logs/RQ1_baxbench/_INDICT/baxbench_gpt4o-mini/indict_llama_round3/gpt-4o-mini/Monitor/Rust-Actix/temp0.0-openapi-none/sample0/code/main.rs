use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use serde::{Deserialize, Serialize};
use std::process::Command;
use regex::Regex;

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

#[post("/monitor/commands")]
async fn monitor_commands(req: web::Json<MonitorRequest>) -> impl Responder {
    let command_regex = &req.command_regex;
    let filter_flags = req.filter_flags.as_deref().unwrap_or("aux");

    // Execute the ps command with the provided filter flags
    let output = Command::new("ps")
        .args(filter_flags.split_whitespace())
        .output();

    match output {
        Ok(output) => {
            let stdout = String::from_utf8_lossy(&output.stdout);
            let regex = Regex::new(command_regex).unwrap();
            let mut processes = Vec::new();

            for line in stdout.lines().skip(1) { // Skip the header line
                let parts: Vec<&str> = line.split_whitespace().collect();
                if let Some(pid_str) = parts.get(1) {
                    if let Ok(pid) = pid_str.parse::<i32>() {
                        let process_string = line.to_string();
                        if regex.is_match(&process_string) {
                            processes.push(ProcessInfo {
                                processId: pid,
                                processString: process_string,
                            });
                        }
                    }
                }
            }

            HttpResponse::Ok().json(processes)
        }
        Err(_) => HttpResponse::InternalServerError().json("Failed to execute command"),
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .service(monitor_commands)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}