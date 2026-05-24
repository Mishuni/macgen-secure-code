Rails.application.routes.draw do
  post '/download', to: 'songs#download'
end