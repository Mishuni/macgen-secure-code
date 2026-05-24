Rails.application.routes.draw do
  post '/login', to: 'authentication_controller#login'
  post '/register', to: 'authentication_controller#register'
end