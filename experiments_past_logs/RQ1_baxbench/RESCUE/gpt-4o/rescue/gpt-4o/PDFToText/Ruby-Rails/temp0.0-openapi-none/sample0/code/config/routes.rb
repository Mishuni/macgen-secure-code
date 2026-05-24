Rails.application.routes.draw do
  post '/convert', to: 'pdf_converter#convert'
end