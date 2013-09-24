# saved as greeting.py

import Pyro4
from twython import Twython
import MySQLdb
import csv

#from funciones import pedirTweetsDiscos
#from funciones import pedirTweetsPeliculas
from funciones import obtenerNEs
from funciones import obtenerDiscos
from funciones import obtenerPeliculas

server_almacenador=Pyro4.Proxy("PYRONAME:quehago.almacenador")    # use name server object lookup uri shortcut

class Procesador(object):

    def __init__(self):
        self.db_host = 'localhost'
        self.db_user = 'root'
        self.db_pass = 'fatigatti'
        self.db_name = 'quehago'
        print "inicializado"
        self.conectar_a_mysql()
        return

    def conectar_a_mysql(self):
         self.db = MySQLdb.connect(host=self.db_host, user=self.db_user, passwd=self.db_pass, db=self.db_name)
         print "conectado a la DB"

    def abrir_cursor(self):
        self.cursor = self.db.cursor()

    def ejecutar_consulta(self, query, values=''):
        if values != '':
            self.cursor.execute(query, values)
        else:
            self.cursor.execute(query)

    def traer_datos(self):
        self.rows = self.cursor.fetchall()

    def send_commit(self, query):
        sql = query.lower()
        if sql.count('select')<1:
            self.db.commit()


    def crear_usuario_en_bd(self, usuario=''):
        if usuario == '':
            return
        self.conectar_a_mysql()
        self.abrir_cursor()
        self.ejecutar_consulta("SELECT nombre_usuario FROM usuarios WHERE nombre_usuario=%s", usuario)

        if self.cursor.rowcount<0:
            self.cerrar_cursor()
            print "Error en la consulta"
            return
        if self.cursor.rowcount<1:
            self.ejecutar_consulta("INSERT INTO usuarios (nombre_usuario, preferencias_peliculas, preferencias_musica) VALUES (%s, '{}', '{}')", usuario)
            self.db.commit()
            print "Usuario Creado"
        else:
            print "Usuario existente"
        self.cerrar_cursor()


    def guardar_recomendaciones_en_bd(self, tabla):
        sugerencias = server_almacenador.get_sugerencias()
        self.conectar_a_mysql()
        self.abrir_cursor()
        if tabla == 'peliculas':
            query = "INSERT INTO peliculas (rating, anio, imdb_id, imdb_url, titulo, sinopsis, poster, generos, idioma, actores, duracion) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
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
                            print pelicula[campo]
                            datoPelicula.append(str(pelicula[campo].encode('utf-8')))
                            print "este anduvo"
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
                    listas = ['genres', 'language','actors', 'runtime']
                    for lista in listas:
                        print lista
                        if lista in pelicula:
                            print ', '.join(pelicula[lista])
                            datoPelicula.append(', '.join(pelicula[lista]))   
                    datos.append(tuple(datoPelicula))
        else:
            if tabla == 'musica':
                query = "INSERT INTO musica (artista, album, anio, imagen, lastfm_url) VALUES (%s, %s, %s, %s, %s)"
                datos = []
            
            # for (tweet, nes, discos) in sugerencias:
            #     for disco in discos:
            #         datoAlbum = []
            # TODO                    

        self.cursor.executemany(query, datos)
        self.db.commit()
        self.cerrar_cursor()
        return str(len(datos))+" registros de "+tabla+" guardados"

    def traer_recomendaciones_personalizadas(self, usuario, tipo):
        resultados = self.traer_recomendaciones_de_bd(tipo)
        objeto_preferencias = self.traer_preferencias_usuario(usuario, tipo)
        print str(objeto_preferencias)

        peliculasConPuntaje = []
        for (id, fecha, titulo, generos, idioma, rating, anio, imdb_id, actores, sinopsis, poster, duracion, imdb_url) in resultados:
            generosArreglo = generos.split(', ')
            puntuacion = 0
            for genero in generosArreglo:
                if genero in objeto_preferencias:
                    puntuacion = puntuacion + objeto_preferencias[genero]
            puntuacionAcotada = str(round((float(puntuacion) / float(2*len(generosArreglo))) + float(2.5),1))
            peliculasConPuntaje.append((puntuacionAcotada, id, fecha, titulo, generos, idioma, rating, anio, imdb_id, actores, sinopsis, poster, duracion, imdb_url))
        
        # Ordenar por columan rating nuestro
        resultadosOrdenados = sorted(peliculasConPuntaje, key=lambda pelicula: pelicula[0], reverse=True)

        return resultadosOrdenados

    def traer_recomendaciones_de_bd(self, tipo):
        self.abrir_cursor()
        self.ejecutar_consulta("SELECT * FROM "+tipo+" ORDER BY fecha desc, rating desc LIMIT 10")
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
                if accion=='aumentar' and objeto_preferencias[genero]<5:
                    objeto_preferencias[genero] += 1
                if accion=='disminuir' and objeto_preferencias[genero]>-5:
                    objeto_preferencias[genero] -= 1
            else:
                if accion=='aumentar':
                    objeto_preferencias[genero] = 1
                if accion=='disminuir':
                    objeto_preferencias[genero] = -1
        self.abrir_cursor()
        print "aca llego"        
        self.ejecutar_consulta("UPDATE usuarios SET preferencias_peliculas=\""+str(objeto_preferencias)+"\" WHERE nombre_usuario=\""+usuario+"\"")
        print "aca no llego"
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
        """Cerrar cursor"""
        self.cursor.close()

    def ejecutar(self, query, values=''):
        """Compilar todos los procesos"""
        # ejecuta todo el proceso solo si las propiedades han sido definidas
        if (self.db_host and self.db_user and self.db_pass and self.db_name and
            query):
            self.conectar_a_mysql()
            self.abrir_cursor()
            self.ejecutar_consulta(query, values)
            self.send_commit(query)
            self.traer_datos()
            self.cerrar_cursor()

            return self.rows

    def conectar_a_twitter(self):
        APP_KEY = '4EDYH92aDYG06Mak7xg'
        APP_SECRET = 'KBNlPuQl0xaTgzbzbMydJXm56fvlPCvEe054pLcmEnc'

        #twitter = Twython(APP_KEY, APP_SECRET, oauth_version=2)
        #ACCESS_TOKEN = twitter.obtain_access_token()
        ACCESS_TOKEN = "AAAAAAAAAAAAAAAAAAAAAM3HQQAAAAAAF2sy4rN%2BQLMBGaBdmreW%2B1TNG7M%3Dl1SB37LUwgctWo3Duvjfuth6r8NpxrkEkFoUuBhnK98"
        self.twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)
        return 

    def obtenerCategoriasArchivo(self, archivo):
        from sets import Set
        try:
            fp = open( archivo, 'rb' )
        except IOError:
            return []

        reader = csv.reader( fp, delimiter=',', quotechar='"', escapechar='\\' )
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
        tweetsNuevos = []
        for status in statuses:
            if not 'RT' in status['text']: # Controlar bien que no sean retweets
                tweetsNuevos.append(h.unescape(status['text']))

        server_almacenador.set_tipo_tweets(tipoTweets)
        server_almacenador.set_tweets(tweetsNuevos)

        if len(tweetsNuevos)>0:
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


servidor_procesador=Procesador()

daemon=Pyro4.Daemon()                 # make a Pyro daemon
ns=Pyro4.locateNS()                   # find the name server
uri=daemon.register(servidor_procesador)   # register the greeting object as a Pyro object
ns.register("quehago.procesador", uri)  # register the object with a name in the name server

print 'Ready.'
daemon.requestLoop()                  # start the event loop of the server to wait for calls
