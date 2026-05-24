Rails.application.routes.draw do
  post '/convert', to: 'application#convert'
end