# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# This file is the source Rails uses to define your schema when running `bin/rails
# db:schema:load`. When creating a new database, `bin/rails db:schema:load` tends to
# be faster and is potentially less error prone than running all of your
# migrations from scratch. Old migrations may fail to apply correctly if those
# migrations use external dependencies or application code.
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema[8.0].define(version: 0) do
  create_table "shopify_products", force: :cascade do |t|
    t.string "title", limit: 255
    t.text "body_html"
    t.string "vendor", limit: 255
    t.string "product_type", limit: 255
    t.datetime "created_at", precision: nil
    t.datetime "updated_at", precision: nil
    t.datetime "published_at", precision: nil
    t.string "handle", limit: 255
    t.string "status", limit: 50
    t.string "published_scope", limit: 50
    t.text "tags"
    t.string "admin_graphql_api_id", limit: 255
    t.integer "total_inventory", default: 0
    t.integer "total_variants", default: 0
    t.integer "total_images", default: 0
    t.integer "total_options", default: 0
  end
end
