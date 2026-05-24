Rails.application.routes.draw do
  post '/convert', to: 'pdf#convert'
end