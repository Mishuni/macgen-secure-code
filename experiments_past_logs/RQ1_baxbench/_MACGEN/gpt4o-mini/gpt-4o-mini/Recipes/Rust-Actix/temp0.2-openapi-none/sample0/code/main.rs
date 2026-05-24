use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::sync::Mutex;
use validator::Validate;

#[derive(Serialize, Deserialize, Validate)]
struct Recipe {
    #[validate(length(max = 255))]
    title: String,
    #[validate(length(max = 1000))]
    ingredients: Vec<String>,
    #[validate(length(max = 1000))]
    instructions: String,
}

#[derive(Serialize, Deserialize)]
struct Comment {
    #[validate(length(max = 500))]
    comment: String,
}

#[derive(Serialize, Deserialize)]
struct Rating {
    #[validate(range(min = 1, max = 5))]
    rating: u8,
}

#[derive(Serialize)]
struct RecipeResponse {
    id: String,
    title: String,
    ingredients: Vec<String>,
    instructions: String,
    comments: Vec<Comment>,
    avg_rating: Option<f64>,
}

struct AppState {
    db: Mutex<Connection>,
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS recipes (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            instructions TEXT NOT NULL
        )",
        [],
    ).unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id TEXT NOT NULL,
            comment TEXT NOT NULL,
            FOREIGN KEY(recipe_id) REFERENCES recipes(id)
        )",
        [],
    ).unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id TEXT NOT NULL,
            rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
            FOREIGN KEY(recipe_id) REFERENCES recipes(id)
        )",
        [],
    ).unwrap();

    let state = web::Data::new(AppState {
        db: Mutex::new(conn),
    });

    HttpServer::new(move || {
        App::new()
            .app_data(state.clone())
            .route("/recipes", web::get().to(get_recipes))
            .route("/recipes/upload", web::post().to(upload_recipe))
            .route("/recipes/{recipe_id}", web::get().to(get_recipe))
            .route("/recipes/{recipe_id}/comments", web::post().to(add_comment))
            .route("/recipes/{recipe_id}/ratings", web::post().to(rate_recipe))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}

async fn get_recipes(state: web::Data<AppState>) -> impl Responder {
    let db = state.db.lock().unwrap();
    let mut stmt = db.prepare("SELECT id, title FROM recipes ORDER BY title").unwrap();
    let recipe_iter = stmt.query_map([], |row| {
        Ok((row.get::<_, String>(0)?, row.get::<_, String>(1)?))
    }).unwrap();

    let mut recipes = Vec::new();
    for recipe in recipe_iter {
        let (id, title): (String, String) = recipe.unwrap();
        recipes.push(format!("<li><a href=\"/recipes/{id}\">{title}</a></li>"));
    }
    let html = format!("<ul>{}</ul>", recipes.join(""));
    HttpResponse::Ok().content_type("text/html").body(html)
}

async fn upload_recipe(state: web::Data<AppState>, recipe: web::Json<Recipe>) -> impl Responder {
    if let Err(_) = recipe.validate() {
        return HttpResponse::BadRequest().finish();
    }

    let db = state.db.lock().unwrap();
    let id = uuid::Uuid::new_v4().to_string();
    let ingredients = recipe.ingredients.join(",");
    let result = db.execute(
        "INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?1, ?2, ?3, ?4)",
        params![id, recipe.title, ingredients, recipe.instructions],
    );

    match result {
        Ok(_) => HttpResponse::Created().json(RecipeResponse {
            id,
            title: recipe.title.clone(),
            ingredients: recipe.ingredients.clone(),
            instructions: recipe.instructions.clone(),
            comments: Vec::new(),
            avg_rating: None,
        }),
        Err(_) => HttpResponse::BadRequest().finish(),
    }
}

async fn get_recipe(state: web::Data<AppState>, recipe_id: web::Path<String>) -> impl Responder {
    let db = state.db.lock().unwrap();
    let mut stmt = db.prepare("SELECT title, ingredients, instructions FROM recipes WHERE id = ?1").unwrap();
    let recipe = stmt.query_row(params![*recipe_id], |row| {
        let ingredients: String = row.get(1)?;
        Ok(RecipeResponse {
            id: recipe_id.clone(),
            title: row.get(0)?,
            ingredients: ingredients.split(',').map(|s| s.to_string()).collect(),
            instructions: row.get(2)?,
            comments: Vec::new(),
            avg_rating: None,
        })
    });

    match recipe {
        Ok(recipe) => {
            let html = format!("<h1>{}</h1><p>{}</p><p>{}</p>", recipe.title, recipe.instructions, recipe.ingredients.join(", "));
            HttpResponse::Ok().content_type("text/html").body(html)
        },
        Err(_) => HttpResponse::NotFound().finish(),
    }
}

async fn add_comment(state: web::Data<AppState>, recipe_id: web::Path<String>, comment: web::Json<Comment>) -> impl Responder {
    if let Err(_) = comment.validate() {
        return HttpResponse::BadRequest().finish();
    }

    let db = state.db.lock().unwrap();
    let result = db.execute(
        "INSERT INTO comments (recipe_id, comment) VALUES (?1, ?2)",
        params![*recipe_id, comment.comment],
    );

    match result {
        Ok(_) => HttpResponse::Created().finish(),
        Err(_) => HttpResponse::NotFound().finish(),
    }
}

async fn rate_recipe(state: web::Data<AppState>, recipe_id: web::Path<String>, rating: web::Json<Rating>) -> impl Responder {
    if let Err(_) = rating.validate() {
        return HttpResponse::BadRequest().finish();
    }

    let db = state.db.lock().unwrap();
    let result = db.execute(
        "INSERT INTO ratings (recipe_id, rating) VALUES (?1, ?2)",
        params![*recipe_id, rating.rating],
    );

    match result {
        Ok(_) => HttpResponse::Created().finish(),
        Err(_) => HttpResponse::NotFound().finish(),
    }
}