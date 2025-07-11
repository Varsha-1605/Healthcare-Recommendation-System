from app import app
import routes  # noqa: F401
import populate_data  # Import the populate_data script


if __name__ == '__main__':
    with app.app_context():
        print("🏥 Running database population script...")
        populate_data.populate_sample_content()
    
        print("✅ Database population complete (if not already populated)!")
    app.run(host='0.0.0.0', port=5000, debug=True)
