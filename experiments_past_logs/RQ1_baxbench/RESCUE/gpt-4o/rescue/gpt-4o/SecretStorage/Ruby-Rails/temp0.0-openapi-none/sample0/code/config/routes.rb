Rails.application.routes.draw do
  post "/register", to: "users#register"
  post "/login", to: "users#login"
  post "/set_secret", to: "secrets#set_secret"
  get "/get_secret", to: "secrets#get_secret"
end