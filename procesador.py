#import pudb; pudb.set_trace()

import Pyro4
from twython import Twython
import MySQLdb
import csv
import time

from funciones import obtenerNEs
from funciones import obtenerDiscos
from funciones import obtenerPeliculas

APP_KEY = 'oyEys6d4bYh3VVMHE8cvAw'
APP_SECRET = 'wqHM5ZuDOQwRmD1VzBjLxHH6pKu9FAfo1gPp7nUSKc4'

server_almacenador = Pyro4.Proxy("PYRONAME:quehago.almacenador")    # use name server object lookup uri shortcut
server_clasificador = Pyro4.Proxy("PYRONAME:quehago.clasificador.sentimientos")    # use name server object lookup uri shortcut
server_clasificador._pyroOneway.add("analizar_sentimientos")

Pyro4.config.ONEWAY_THREADED = True


class Procesador(object):

    def __init__(self):
        self.conectar_a_mysql()
        return

    def conectar_a_mysql(self):
        db_host = 'localhost'
        db_user = 'root'
        db_pass = 'fatigatti'
        db_name = 'quehago'
        self.db = MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_name)
        print "conectado a la DB"

    def abrir_cursor(self):
        self.cursor = self.db.cursor()

    def ejecutar_consulta(self, query, values=''):
        if values != '':
            self.cursor.execute(query, values)
        else:
            self.cursor.execute(query)

    def actualizar_timeline(self, usuario):
        # import locale
        # locale.setlocale(locale.LC_TIME, "en_US")
        from dateutil.parser import parse
        sinceID = 0

        ## Obtenemos el id del ultimo tweet ya bajado ##
        self.abrir_cursor()
        query = "SELECT MAX(tweetID) FROM timeline_"+str(usuario)
        self.ejecutar_consulta(query)

        if self.cursor.rowcount < 0:
            self.cerrar_cursor()
            print "Error en la consulta"
            return

        resultados = self.cursor.fetchone()

        sinceID = resultados[0] or 1

        ## Obtenemos los datos de acceso del usuario ##
        self.abrir_cursor()
        self.ejecutar_consulta("SELECT oauth_token, oauth_token_secret FROM usuarios WHERE nombre_usuario=%s", usuario)
        resultados = self.cursor.fetchone()
        oauth_token = resultados[0]
        oauth_token_secret = resultados[1]

        ## Obtenemos el objeto de acceso a Twitter ##
        twitter = Twython(APP_KEY, APP_SECRET, oauth_token, oauth_token_secret)

        ## Inicio de minado de tweets
        MAX_PAGES = 4

        resultados = twitter.get_home_timeline(since_id=sinceID, count=200, include_rts=False)

        listaTweets = []
        for res in resultados:
            if res['user']['screen_name'].lower() != usuario.lower():
                created_at = str(res['created_at'].encode('utf-8'))
                fecha = parse(created_at).strftime('%Y-%m-%d')
                listaTweets.append(
                    (
                        str(res['id_str']),
                        str(res['text'].encode('utf-8')),
                        fecha
                    )
                )

        self.abrir_cursor()
        query = "INSERT INTO timeline_"+str(usuario)+"(tweetID, tweetTexto, tweetFecha) VALUES(%s, %s, %s)"

        self.cursor.executemany(query, listaTweets)
        self.db.commit()
        self.cerrar_cursor()

        print "Termino pagina 1"

        page_num = 1
        while page_num < MAX_PAGES and len(resultados) > 0:
            listaTweets = []
            max_id = min([tweet['id'] for tweet in resultados])
            resultados = twitter.get_home_timeline(since_id=sinceID, count=200,
                                                   include_rts=False, max_id=max_id)
            page_num += 1

            for res in resultados:
                if res['user']['screen_name'].lower() == usuario.lower():
                    continue
                created_at = str(res['created_at'].encode('utf-8'))
                fecha = parse(created_at).strftime('%Y-%m-%d')
                listaTweets.append(
                    (
                        str(res['id_str']),
                        str(res['text'].encode('utf-8')),
                        fecha
                    )
                )

            self.abrir_cursor()

            self.cursor.executemany(query, listaTweets[1:])
            self.db.commit()
            self.cerrar_cursor()

            print "Termino pagina "+str(page_num)
        print "todo guardado"
        self.clasificarTweets(usuario)

    def clasificarTweets(self, usuario):
        self.abrir_cursor()
        self.ejecutar_consulta("SELECT tweetID, tweetFecha FROM timeline_"+str(usuario)+" WHERE clasificacion IS NULL")
        if self.cursor.rowcount > 0:
            resultados = self.cursor.fetchall()
        self.cerrar_cursor()
        tweetsClasificados = server_clasificador.analizar_sentimientos(resultados, True)
        # Insertar tweets en bd
        return

    def crear_usuario_en_bd(self, usuario='', oauth_token='', oauth_token_secret=''):
        print "iniciando crear usuario"
        if usuario == '':
            return -1
        self.abrir_cursor()
        self.ejecutar_consulta("SELECT nombre_usuario FROM usuarios WHERE nombre_usuario=%s", usuario)

        if self.cursor.rowcount < 0:
            self.cerrar_cursor()
            print "Error en la consulta"
            return -1
        if self.cursor.rowcount == 0:

            query = "INSERT INTO usuarios(nombre_usuario, preferencias_peliculas, preferencias_musica, \
                            oauth_token, oauth_token_secret) VALUES(%s, '{}', '{}', %s, %s)"
            self.ejecutar_consulta(query, [usuario, oauth_token, oauth_token_secret])
            self.db.commit()

            query = "CREATE TABLE timeline_"+str(usuario)+"(tweetID VARCHAR(25) PRIMARY KEY, tweetTexto TEXT, \
                        tweetFecha DATE, clasificacion VARCHAR(15))"
            self.ejecutar_consulta(query)
            self.db.commit()

            print "Usuario Creado"
            return 1
        else:
            print "Usuario existente"
            return 0
        self.cerrar_cursor()

    def guardar_recomendaciones_en_bd(self):
        tabla = server_almacenador.get_tipo_tweets()
        sugerencias = server_almacenador.get_sugerencias()
        self.abrir_cursor()
        if tabla == 'peliculas':
            query = "INSERT INTO peliculas (rating, anio, imdb_id, imdb_url, titulo, sinopsis, \
                                            poster, generos, idioma, actores, duracion) \
                     VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

            datos = []
            for (tweet, nes, peliculas) in sugerencias:
                for pelicula in peliculas:
                    datoPelicula = []

                    if 'rating' in pelicula:
                        datoPelicula.append(str(pelicula['rating']))
                    else:
                        datoPelicula.append('')

                    camposTextoSimple = ['year', 'imdb_id', 'imdb_url']
                    for campo in camposTextoSimple:
                        if campo in pelicula:
                            datoPelicula.append(pelicula[campo])
                        else:
                            datoPelicula.append('')

                    camposTexto = ['title', 'plot_simple']
                    for campo in camposTexto:
                        if campo in pelicula:
                            datoPelicula.append(str(pelicula[campo].encode('utf-8')))
                        else:
                            datoPelicula.append('')
                    if 'poster' in pelicula:
                        if 'imdb' in pelicula['poster']:
                            datoPelicula.append(pelicula['poster']['imdb'])
                        else:
                            if 'cover' in pelicula['poster']:
                                datoPelicula.append(pelicula['poster']['cover'])
                            else:
                                datoPelicula.append('')
                    else:
                        datoPelicula.append('')
                    listas = ['genres', 'language', 'actors', 'runtime']
                    for lista in listas:
                        if lista in pelicula:
                            datoPelicula.append(', '.join(pelicula[lista]))
                    datos.append(tuple(datoPelicula))
        else:
            if tabla == 'musica':
                query = "INSERT INTO musica (artista, album, imagen, lastfm_url) VALUES (%s, %s, %s, %s)"
                datos = []

                for (tweet, nes, discos) in sugerencias:
                    for disco in discos:
                        datoAlbum = []
                        datoAlbum.append(str(disco['artist'].encode('utf-8')))
                        datoAlbum.append(str(disco['name'].encode('utf-8')))
                        imagenes = disco['image']
                        for imagen in imagenes:
                            if imagen['size'] == 'large':
                                datoAlbum.append(str(imagen['#text']))
                        datoAlbum.append(str(disco['url']))
                        datos.append(tuple(datoAlbum))

        self.cursor.executemany(query, datos)
        self.db.commit()
        self.cerrar_cursor()
        return str(len(datos))+" registros de "+tabla+" guardados"

    def traer_recomendaciones_personalizadas(self, usuario, tipo):
        resultados = self.traer_recomendaciones_de_bd(tipo)
        objeto_preferencias = self.traer_preferencias_usuario(usuario, tipo)

        if tipo == 'peliculas':
            peliculasConPuntaje = []
            for (id, fecha, titulo, generos, idioma, rating, anio,
                 imdb_id, actores, sinopsis, poster, duracion, imdb_url) in resultados:
                generosArreglo = generos.split(', ')
                puntuacion = 0
                for genero in generosArreglo:
                    if genero in objeto_preferencias:
                        puntuacion = puntuacion + objeto_preferencias[genero]
                puntuacionAcotada = str(round((float(puntuacion) / float(2*len(generosArreglo))) + float(2.5), 1))
                peliculasConPuntaje.append((puntuacionAcotada, id, fecha, titulo, generos, idioma,
                                            rating, anio, imdb_id, actores, sinopsis, poster, duracion, imdb_url))
            # TODO: que ordene por fecha ademas de rating
            resultadosOrdenados = sorted(peliculasConPuntaje, key=lambda pelicula: pelicula[0], reverse=True)

        if tipo == 'musica':
            resultadosOrdenados = resultados
            # discosConPuntaje = []
            # for (id, artista, album, imagen, lastfm_url) in resultados:
            #     #generosArreglo = generos.split(', ')
            #     puntuacion = 0
            #     for genero in generosArreglo:
            #         if genero in objeto_preferencias:
            #             puntuacion = puntuacion + objeto_preferencias[genero]
            #     puntuacionAcotada = str(round((float(puntuacion) / float(2*len(generosArreglo))) + float(2.5), 1))
            #     peliculasConPuntaje.append((puntuacionAcotada, id, fecha, titulo, generos, idioma,
            #                                 rating, anio, imdb_id, actores, sinopsis, poster, duracion, imdb_url))

        # Ordenar por columan rating nuestro


        return resultadosOrdenados

    def traer_recomendaciones_de_bd(self, tipo):
        self.abrir_cursor()
        #self.ejecutar_consulta("SELECT * FROM "+tipo+" ORDER BY fecha desc, rating desc LIMIT 10")
        self.ejecutar_consulta("SELECT * FROM "+tipo+" LIMIT 10")
        resultados = self.cursor.fetchall()
        self.cerrar_cursor()
        return resultados

    def traer_generos_pelicula_de_bd(self, id):
        self.abrir_cursor()
        self.ejecutar_consulta("SELECT generos FROM peliculas WHERE id="+id)
        resultados = self.cursor.fetchall()
        return resultados[0][0]

    def traer_preferencias_usuario(self, usuario, tipo):
        import ast
        self.abrir_cursor()
        self.ejecutar_consulta("SELECT preferencias_"+tipo+" FROM usuarios WHERE nombre_usuario=%s", usuario)
        resultados = self.cursor.fetchone()
        return ast.literal_eval(resultados[0])

    def actualizar_puntaje(self, peliculaId, usuario, accion):
        generos = self.traer_generos_pelicula_de_bd(peliculaId)
        objeto_preferencias = self.traer_preferencias_usuario(usuario, 'peliculas')

        generosArreglo = generos.split(', ')
        for genero in generosArreglo:
            if genero in objeto_preferencias:
                if accion == 'aumentar' and objeto_preferencias[genero] < 5:
                    objeto_preferencias[genero] += 1
                if accion == 'disminuir' and objeto_preferencias[genero] > -5:
                    objeto_preferencias[genero] -= 1
            else:
                if accion == 'aumentar':
                    objeto_preferencias[genero] = 1
                if accion == 'disminuir':
                    objeto_preferencias[genero] = -1
        self.abrir_cursor()
        self.ejecutar_consulta("UPDATE usuarios SET preferencias_peliculas=\"" + str(objeto_preferencias) + "\" \
                                WHERE nombre_usuario=\""+usuario+"\"")
        self.db.commit()
        self.cerrar_cursor()

    def actualizar_objeto_puntaje(self, objeto_puntaje, pelicula, gusto):
        for genero in pelicula:
            if gusto:
                objeto_puntaje['genero'] += 1
            else:
                objeto_puntaje['genero'] += -1
        return objeto_puntaje

    def cerrar_cursor(self):
        self.cursor.close()

    def conectar_a_twitter(self):
        APP_KEY = '4EDYH92aDYG06Mak7xg'
        #APP_SECRET = 'KBNlPuQl0xaTgzbzbMydJXm56fvlPCvEe054pLcmEnc'
        ACCESS_TOKEN = "AAAAAAAAAAAAAAAAAAAAAM3HQQAAAAAAF2sy4rN%2BQLMBGaBdmreW%2B1TNG7M%3Dl1SB37LUwgctWo3Duvjfuth6r8NpxrkEkFoUuBhnK98"
        self.twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)
        return

    def obtenerCategoriasArchivo(self, archivo):
        try:
            fp = open(archivo, 'rb')
        except IOError:
            return []

        reader = csv.reader(fp, delimiter=',', quotechar='"', escapechar='\\')
        categorias = set()
        for row in reader:
            categorias.add(row[1])
        return list(categorias)

    def obtener_tweets(self, termino, tipoTweets):
        print "tipo de tweets: "+tipoTweets
        results = self.twitter.search(q=termino, lang='en', count=100)

        import HTMLParser
        h = HTMLParser.HTMLParser()

        # Hacemos una busqueda
        statuses = results['statuses']

        if tipoTweets == 'entrenamiento':

            tweetsNuevos = []
            for status in statuses:
                if not 'RT' in status['text']:  # Controlar bien que no sean retweets
                    tweetsNuevos.append((status['id'], h.unescape(status['text'])))
            return tweetsNuevos

        else:
            tweetsNuevos = []
            for status in statuses:
                if not 'RT' in status['text']:  # Controlar bien que no sean retweets
                    tweetsNuevos.append(h.unescape(status['text']))

        server_almacenador.set_tipo_tweets(tipoTweets)
        server_almacenador.set_tweets(tweetsNuevos)

        if tweetsNuevos:
            return "Hubo "+str(len(tweetsNuevos))+" resultados"
        return "No hubo resultados"

    def obtener_nes(self):
        try:
            tweetsClasificados = server_almacenador.get_tweets_clasificados()
            nes = obtenerNEs(tweetsClasificados)
            server_almacenador.set_nes(nes)
            return "Nes almacenados"
        except NameError:
            print "Antes de ejecutar esta funcion debe hacer analisis de sentimientos"

    def obtener_sugerencias(self):
        try:
            tipoTweets = server_almacenador.get_tipo_tweets()
            nes = server_almacenador.get_nes()
            if tipoTweets == "musica":
                server_almacenador.set_sugerencias(obtenerDiscos(nes))
                return "Sugerencias almacenadas"
            if tipoTweets == "peliculas":
                server_almacenador.set_sugerencias(obtenerPeliculas(nes))
                return "Sugerencias almacenadas"
        except NameError:
            print "Antes de ejecutar esta funcion debe ejecutar el entity extractor"
        return "No entro a nada"


servidor_procesador = Procesador()

daemon = Pyro4.Daemon()                 # make a Pyro daemon
ns = Pyro4.locateNS()                   # find the name server
uri = daemon.register(servidor_procesador)   # register the greeting object as a Pyro object
ns.register("quehago.procesador", uri)  # register the object with a name in the name server

print 'Ready.'
daemon.requestLoop()                  # start the event loop of the server to wait for calls
