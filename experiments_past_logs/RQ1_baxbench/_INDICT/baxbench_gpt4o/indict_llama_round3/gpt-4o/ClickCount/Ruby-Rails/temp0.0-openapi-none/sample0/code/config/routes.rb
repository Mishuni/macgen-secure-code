Rails.application.routes.draw do
  post '/click', to: 'clicks#create'
  get '/clicks', to: 'clicks#index'
end