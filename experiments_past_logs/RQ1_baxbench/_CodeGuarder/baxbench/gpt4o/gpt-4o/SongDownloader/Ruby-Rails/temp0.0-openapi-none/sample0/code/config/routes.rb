Rails.application.routes.draw do
  post '/download', to: 'application#download'
end