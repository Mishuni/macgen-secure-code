class CreateServices < ActiveRecord::Migration[8.0]
  def change
    create_table :services do |t|
      t.string :service_id, null: false
      t.string :token_digest, null: false
      t.datetime :last_notification

      t.timestamps
    end

    add_index :services, :service_id
  end
end