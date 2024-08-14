from flask import Flask, render_template, request, redirect, url_for
import time 
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'  # Ruta del archivo de base de datos SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#declaramos la base de datos
db = SQLAlchemy(app)


# Modelo de base de datos para almacenar datos y tiempos

class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(100), unique=True, nullable=False)
    timestamp = db.Column(db.Float, nullable=False) 
    processed = db.Column(db.Boolean, default=False)
    category = db.Column(db.String(50), nullable=False)
    minute_count = db.Column(db.Integer, default=0)

@app.route('/', methods=['GET', 'POST'])
def index():
    search_result = None
    if request.method == 'POST':
        if 'save' in request.form:
            # al presionar el boton guardar, el dato se almacena en la matriz
            new_data = request.form.get('inse')
            category = request.form.get('category')
            #toma el dato de la entrada de texto out, si hay dato lo arroja, en caso contrario se indica que no esta
            if not category:
                search_result = "Por favor, selecciona una categoría válida."
            elif new_data:
                existing_data = Data.query.filter_by(value=new_data).first()
                if existing_data:
                    existing_data.timestamp = time.time()
                    existing_data.processed = False
                    existing_data.category = category

                else:

                    search_category = request.form.get('category')
                    new_entry = Data(value=new_data, timestamp=time.time(), category=category)
                    db.session.add(new_entry)   


                    # Crear un nuevo registro si el dato no existe
                    
                db.session.commit()
        if 'search' in request.form:
            
            # Buscar el dato en la base de datos
            search_query = request.form.get('out')            
            search_category = request.form.get('search_category')
        

            if search_query:
                entry = Data.query.filter_by(value=search_query).first()
      

                if entry:
                    category=entry.category
                    if not entry.processed:
                        start_time = entry.timestamp
                        elapsed_time = time.time() - start_time
                        minutes, seconds = divmod(int(elapsed_time), 60)
                        elapsed_str = f"{minutes} minutos y {seconds} segundos"
                        
                        minute_count = int(elapsed_time // 60)
                        entry.minute_count = minute_count
                        entry.processed = True
                        db.session.commit()
                        

                        search_result = (
                            f"'{search_query}' encontrado en la categoría '{category}'. "
                            f"Tiempo transcurrido: {elapsed_str}. Minutos contados: {minute_count}."
                        )
                    else:
                        search_result = f"'{search_query}' en la categoría '{search_category}' ya ha sido procesado anteriormente."

            else:
                search_result = "Por favor, proporciona tanto el número como la categoría antes de buscar."
    
        if 'entrada' in request.form:
            search_in=request.form.get('nores')
            entry_2=Data.query.filter_by(value=search_in).first()
            
            if entry_2:

                    current_time = time.time()
                    elapsed_time = current_time- entry_2.timestamp
                    minutes, seconds = divmod(int(elapsed_time), 60)
                    elapsed_str = f"{minutes} minutos y {seconds} segundos"
                    
                    minute_count = int(elapsed_time // 60)
                    entry_2.timestamp=current_time
                    entry_2.minute_count=minute_count
                    entry_2.processed = False
                    db.session.commit()

                    
                
            else:
                new_entry2 = Data(value=search_in, timestamp=time.time(),category="no residente")
                db.session.add(new_entry2)
                db.session.commit()
                        

                
            
    
            
    return render_template('index.html', search_result=search_result)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crea las tablas en la base de datos
    app.run(debug=True)
@app.route('/view_all')
def view_all():
    all_data = Data.query.all()  # Obtener todos los registros de la base de datos
    return render_template('view_all.html', all_data=all_data)