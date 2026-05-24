Rails.application.routes.draw do
  post '/extract', to: 'videos#extract'
end