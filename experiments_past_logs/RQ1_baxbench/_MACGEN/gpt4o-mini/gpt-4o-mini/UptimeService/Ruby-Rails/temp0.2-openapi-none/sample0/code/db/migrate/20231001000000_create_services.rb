class CreateServices < ActiveRecord::Migration[7.0]
  def change
    create_table :services do |t|
      t.string :serviceId, null: false, unique: true
      t.string :token, null: false
      t.datetime :lastNotification, null: false

      t.timestamps
    end
  end
end