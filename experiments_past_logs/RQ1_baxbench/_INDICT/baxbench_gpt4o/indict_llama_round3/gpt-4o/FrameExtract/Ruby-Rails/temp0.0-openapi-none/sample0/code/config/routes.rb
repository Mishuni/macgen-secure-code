Rails.application.routes.draw do
  post '/extract', to: 'extract#create'
end