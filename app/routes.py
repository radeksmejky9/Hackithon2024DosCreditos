from app import app
@app.route('/')
def index():
    return "Hello, Open Data Processing with Flask!"
