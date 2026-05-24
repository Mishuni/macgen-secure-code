class CreateInvitations < ActiveRecord::Migration[8.0]
  def change
    create_table :invitations do |t|
      t.string :email, null: false, unique: true
      t.string :invite_id, null: false, unique: true

      t.timestamps
    end
  end
end