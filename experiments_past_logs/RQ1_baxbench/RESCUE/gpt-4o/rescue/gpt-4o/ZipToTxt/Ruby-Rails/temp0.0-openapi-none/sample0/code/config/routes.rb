Rails.application.routes.draw do
  post '/convert', to: 'convert#convert'
end