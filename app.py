from app import create_app

if __name__ == '__main__':
    IP = "10.0.40.21"
    PORT = 8150
    app = create_app()
    app.run(host=IP, port=PORT, debug=True, use_reloader=False)