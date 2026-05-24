Rails.application.routes.draw do
  post '/upload', to: 'images#create'
  get '/images/:imageId', to: 'images#show'
end