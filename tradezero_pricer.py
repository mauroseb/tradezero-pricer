from tradezero_pricer import create_app

application = create_app('container')

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=8080)
