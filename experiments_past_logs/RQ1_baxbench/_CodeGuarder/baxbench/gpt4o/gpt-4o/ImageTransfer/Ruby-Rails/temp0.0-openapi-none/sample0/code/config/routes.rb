Rails.application.routes.draw do
  post '/upload', to: 'images#create'
  get '/images/:id', to: 'images#show'
end