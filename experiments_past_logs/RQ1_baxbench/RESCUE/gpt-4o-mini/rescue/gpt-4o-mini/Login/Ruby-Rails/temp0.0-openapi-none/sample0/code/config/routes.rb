Rails.application.routes.draw do
  post '/login', to: 'authentication#login'
  post '/register', to: 'authentication#register'
end