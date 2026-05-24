Rails.application.routes.draw do
  post '/extract', to: 'frames#extract'
end