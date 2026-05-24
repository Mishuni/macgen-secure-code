Rails.application.routes.draw do
  post '/add', to: 'products#create'
  get '/download', to: 'products#download'
  post '/upload', to: 'products#upload'
  get '/search', to: 'products#search'
end