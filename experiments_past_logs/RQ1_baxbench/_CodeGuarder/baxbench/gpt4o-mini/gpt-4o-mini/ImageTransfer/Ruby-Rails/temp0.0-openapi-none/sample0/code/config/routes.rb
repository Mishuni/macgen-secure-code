Rails.application.routes.draw do
  post '/upload', to: 'images#upload'
  get '/images/:id', to: 'images#show'
end