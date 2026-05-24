Rails.application.routes.draw do
  post 'merchants/register', to: 'merchants#register'
  post 'merchants/login', to: 'merchants#login'
  post 'merchants/upload-wares', to: 'merchants#upload_wares'
  get 'wares', to: 'wares#index'
end