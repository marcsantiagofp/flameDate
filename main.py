from app import create_app

app = create_app()

# Crear las tablas de la base de datos si no existen
with app.app_context():
    from app import models  # Asegura que los modelos estén importados
    models.db.create_all()

# ARRANCADO DEL PROGRAMA
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=81, debug=True)