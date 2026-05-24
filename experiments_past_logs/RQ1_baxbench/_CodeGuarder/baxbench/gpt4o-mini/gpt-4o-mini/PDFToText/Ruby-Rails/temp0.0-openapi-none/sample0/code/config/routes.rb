Rails.application.routes.draw do
  post '/convert', to: 'pdfs#convert'
end