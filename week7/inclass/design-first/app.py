import connexion

app = connexion.FlaskApp(__name__, specification_dir=".")
app.add_api("products.yaml", validate_responses=True)

if __name__ == "__main__":
    app.run(port=5000)