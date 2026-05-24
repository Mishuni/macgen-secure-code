Rails.application.routes.draw do
  post '/merchants/register', to: 'merchants#register'
  post '/merchants/login', to: 'merchants#login'
  post '/merchants/upload-wares', to: 'wares#upload'
  get '/wares', to: 'wares#index'
end