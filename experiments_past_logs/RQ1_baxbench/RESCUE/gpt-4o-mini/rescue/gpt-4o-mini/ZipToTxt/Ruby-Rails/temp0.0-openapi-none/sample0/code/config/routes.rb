Rails.application.routes.draw do
  post '/convert', to: 'conversion#convert'
end