# Localiza SIM
# 
# Sistema desenvolvido para o Hackathon da Liga i9, realizado em outubro de 2017.
# O sistema busca suprir a demanda por visualizacao de dados sobre os onibus na internet
# Os ideias sao a facilidade de uso, eficiencia e manutencao simples
# 
# v0idpwn.github.io

import os
import sqlite3
from flask import Flask, current_app, request, render_template, g, redirect, abort, session, flash, url_for
import json
from geojson import Feature, Point, FeatureCollection, LineString

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'locasim.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASK_SETTINGS', silent=True)


# database functions 
def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv
    
def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    init_db()
    print('Initialized the database.')    
    
def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db
    
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()    


########################################################################

# Pagina inicial, onde eh selecionada a rota
@app.route('/')
def step1():
	db = get_db()
	routes = db.execute('SELECT route_name, route_id from routes')
	routes = routes.fetchall()
	return render_template('selection1.html', routes = routes)


# Pagina onde eh selecionada a direcao
@app.route('/step2/', methods=['POST', 'GET'])
def step2():
	if request.method == 'POST':
		db = get_db()
		schedules = db.execute('SELECT DISTINCT sch_begin, sch_end FROM schedules WHERE route_fk=? AND NOT sch_period = ?', [request.form['route_id'], request.form['period']])
		schedules = schedules.fetchall()
		return render_template('selection2.html', schedules = schedules, period = request.form['period']) 

# Pagina que mostra os links dos horarios de acordo com o que foi selecionado previamente
@app.route('/step3/', methods=['POST', 'GET'])
def step3():
	if request.method == 'POST':
		db = get_db() ############ adicionar sch_obs
		schedules = db.execute('SELECT traj_id, sch_time, sch_bus FROM schedules WHERE sch_begin = ? AND sch_end = ? AND NOT sch_period = ?',[request.form['begin'], request.form['end'], request.form['period']])
		schedules = schedules.fetchall()
		return render_template('selection3.html', schedules = schedules)

# Pagina de visualizacao de rota
@app.route('/view/<traj_id>/<bus_id>', methods=['POST', 'GET'])
def mapView(traj_id, bus_id):
	db = get_db()
	filename = db.execute('SELECT traj_filename FROM trajs WHERE traj_id = ?', [str(traj_id)])
	filename = filename.fetchone()
	f = open('geojson/' + str(filename[0]) + '.geojson', 'r')
	geoJsonString = f.read()
	geoJsonString = geoJsonString.replace('\n', '')
	busUrl = '/position/' + str(bus_id)
	#busUrl = 'https://wanderdrone.appspot.com/'
	return render_template('map.html', geoJsonString = geoJsonString, busUrl = busUrl)
	
	
########################################################################
# paginas de administracao

# pagina default do admin
@app.route('/admin', methods=['POST', 'GET'])
def admin():
	if not session.get('logged_in'):
		abort(401)
	return render_template('admin1.html')


# nessa pagina o administrador pode adicionar caminhos a serem escolhidos
@app.route('/admin/addRoute', methods=['POST', 'GET'])
def addRoute():
	if not session.get('logged_in'):
		abort(401)
	if request.method == 'POST':
		db = get_db()
		db.execute('INSERT INTO routes (route_name) VALUES (?)' , [request.form['name']])
		db.commit()
		return render_template('addRoute.html')
	else:
		return render_template('addRoute.html')


# nessa pagina o administrador cria as trajetorias, que sao os caminhos que o onibus cruza durante sua viagem
@app.route('/admin/addTraj', methods=['POST', 'GET'])
def addTraj():
	if not session.get('logged_in'):
		abort(401)
	db = get_db()
	if request.method == 'POST':
		# obtencao dos dados via POST
		name = request.form['name']
		filename = request.form['filename']
		feature  = []
		latitude = []
		longitude= []
		stops =	[]
		stop  = []
		line  = []
		latitude = request.form.getlist('lat[]')
		longitude = request.form.getlist('lon[]')
		stops = request.form.getlist('selected_stops[]')
		
		# Criando objeto da linha que representa a trajetoria
		for i in range (0, len(latitude)):
			line.append([float(longitude[i]),float(latitude[i])])
		Line = LineString(line)
				
		# Criando os pontos de inicio e fim
		feature.append(Feature(geometry=Point(line[0]), properties={"type": "Inicio", "name" : "Inicio"}))
		feature.append(Feature(geometry=Point(line[len(line)-1]), properties={"type": "Fim", "name":"Fim"}))
		
		# Criando os objetos dos pontos. Stop eh uma lista com listas de
		# 3 membros nas quais o primeiro membro eh a latitude e o segundo a longitude, e o terceiro eh o nome do ponto 
		for i in range(0,len(stops)):
			cur = db.execute('SELECT stop_latitude, stop_longitude, stop_name FROM stops WHERE stop_id=?', [str(stops[i])])
			cur = cur.fetchall()
			feature.append(Feature(geometry=Point([cur[0][1],cur[0][0]]), properties={"type": "parada", "name":cur[0][2]}))
		
		# Por fim adicionando a linha		
		feature.append(Feature(geometry=Line))

		# Criando feature collection e escrevendo no arquivo geojson.
		traj = FeatureCollection(feature)
		f = open('geojson/'+str(filename)+'.geojson', 'w+')
		f.write(str(traj))
		f.close()
		
		# Registrando no banco de dados
		db.execute('INSERT INTO trajs (traj_name,traj_filename) VALUES (?,?)',[str(name),str(filename)])
		db.commit()
		return render_template('admin1.html')
	else:
		stops = db.execute('SELECT stop_id, stop_name FROM stops') 
		stops = stops.fetchall()
		return render_template('addTraj.html', stops=stops)

		
#pagina de criacao de pontos
@app.route('/admin/addStop', methods=['POST', 'GET'])
def addStop():
	if not session.get('logged_in'):
		abort(401)
	if request.method == 'POST':
		db = get_db()
		name = request.form['name']
		lat = request.form['lat']
		lon = request.form['lon']
		db.execute('INSERT INTO stops (stop_name, stop_latitude, stop_longitude) VALUES (?,?,?)', [name, lat, lon])
		db.commit()
		return render_template('addStop.html')
	else:
		return render_template('addStop.html')

#pagina de criacao de onibus
@app.route('/admin/addBus', methods=['POST', 'GET'])
def addBus():
	if not session.get('logged_in'):
		abort(401)
	if request.method == 'POST':
		db = get_db()
		name = request.form['name']
		db.execute('INSERT INTO bus (bus_name) VALUES (?)', [str(name)])
		db.commit()
		return render_template('addBus.html')
	else:
		return render_template('addBus.html')


#pagina de criacao de horarios
@app.route('/admin/addSch', methods=['POST','GET'])
def addSch():
	if not session.get('logged_in'):
		abort(401)
	if request.method == 'POST':
		db = get_db()
		route_id = request.form['route']
		sch_time = request.form['time']
		begin = request.form['begin']
		end = request.form['end']
		period = request.form['period']
		bus_id = request.form['bus_id']
		traj_id = request.form['traj_id']
		desc = request.form['desc']
		db.execute('INSERT INTO schedules (route_fk, sch_time, sch_begin, sch_end, sch_period, sch_bus, traj_id, sch_desc) VALUES (?,?,?,?,?,?,?,?)', [route_id, sch_time, begin, end, period, bus_id, traj_id, desc])
		db.commit()
		return render_template('admin1.html')
	else:
		db = get_db()
		routes = db.execute('SELECT route_id, route_name FROM routes')
		routes = routes.fetchall()
		trajs = db.execute('SELECT traj_id, traj_name FROM trajs')
		trajs = trajs.fetchall()
		buses = db.execute('SELECT bus_id, bus_name FROM bus')
		buses = buses.fetchall()
		return render_template('addSch.html', routes = routes, trajs = trajs, buses = buses)

#pagina para onde sao enviados os requests com os dados do busao
@app.route('/position/<bus_id>', methods=['POST','GET'])
def busUpdate(bus_id):
	if request.method == 'POST':
		db = get_db()
		dTime = request.form['time']
		lat = request.form['lat']
		lon = request.form['lon']
		db.execute('INSERT INTO bus_data (bus_id, last_latitude, last_longitude, last_time) VALUES (?,?,?,?)', [str(bus_id), float(lat), float(lon), str(dTime)])
		db.commit()
		return "sucess"
	else:
		db = get_db()
		bus_data = db.execute('SELECT last_latitude, last_longitude, last_time FROM bus_data WHERE bus_id = ? ORDER BY data_id DESC LIMIT 1', [str(bus_id)])
		bus_data = bus_data.fetchall()
		busGeoJson = {"geometry": {"type": "Point", "coordinates": [bus_data[0][1], bus_data[0][0]]}, "type": "Feature", "properties": {"time":str(bus_data[0][2])}}
		return str(busGeoJson).replace("'",'"')

#pagina de login do administrador
@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		if request.form['username'] != app.config['USERNAME']:
			abort()
		elif request.form['password'] != app.config['PASSWORD']:
			abort()
		else:
			session['logged_in'] = True
			flash('You were logged in')
			return redirect(url_for('admin'))
	return render_template('login.html')
