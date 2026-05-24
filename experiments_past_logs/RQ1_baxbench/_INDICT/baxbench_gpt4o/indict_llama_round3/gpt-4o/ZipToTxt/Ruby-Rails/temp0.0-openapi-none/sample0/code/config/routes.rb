<FILEPATH>
config/routes.rb
</FILEPATH>
<CODE>
Rails.application.routes.draw do
  post '/convert', to: 'convert#create'
end
</CODE>