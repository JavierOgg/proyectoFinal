import web
# import logging
import json
import Pyro4

server_clasificador=Pyro4.Proxy("PYRONAME:quehago.clasificador")    # use name server object lookup uri shortcut
server_procesador=Pyro4.Proxy("PYRONAME:quehago.procesador")    # use name server object lookup uri shortcut
server_almacenador=Pyro4.Proxy("PYRONAME:quehago.almacenador")    # use name server object lookup uri shortcut

def imprimirlindo(texto):
    return json.dumps(texto, sort_keys=True, indent=4)

# render = web.template.render('templates/', globals={'imprimir':imprimirlindo})
render = web.template.render('templates/', globals={'imprimir':imprimirlindo, 'tipo': type})
app_render = web.template.render('templates/app', globals={'imprimir':imprimirlindo})
usuario_render = web.template.render('templates/usuario')


APP_KEY = 'oyEys6d4bYh3VVMHE8cvAw'
APP_SECRET = 'wqHM5ZuDOQwRmD1VzBjLxHH6pKu9FAfo1gPp7nUSKc4'

urls = (
    '/', 'index',
    '/login', 'loginUsuario',
    '/profile', 'profile',
    '/admin', 'app_login',
    '/admin/utilidades/(.*)', 'utilidades',
    '/interaccion_usuario/(.*)', 'interaccion_usuario',
    '/usuario/logout', 'logout',
    '/usuario/profile/(.*)', 'profile_sinlogin',
    '/usuario/logincallback', 'logincallback',
    '/usuario/mine_usertimeline', 'mineusertimeline',
    '/usuario/analizar_frecuencia', 'analizarfrecuencia',
    '/usuario/listar_tweets', 'listartweets',
    '/app/test', 'app_conectar',
    '/admin/entrenamiento', 'app_entrenamiento',
    '/app/sugerencias_peliculas', 'app_sugerencias_peliculas',    
    '/app/sugerencias_musica', 'app_sugerencias_musica',    
    '/app/buscar', 'app_buscar',
    '/app/profile', 'app_profile',
    '/app/mine_hometimeline', 'app_minehometimeline',
    '/app/mine_usertimeline', 'app_mineusertimeline',
    '/app/analizar_frecuencia', 'app_analizarfrecuencia',
    '/app/listar_tweets', 'app_listartweets',
)

app = web.application(urls, globals())

if web.config.get('_session') is None:
    session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={
                                  'oauth_token': '',
                                  'oauth_token_secret': '',
                                  'auth_tokens': '',
                                  'app_access_token':'',
                                  'screen_name' : '',
                                  'id' : ''
                                  })
    web.config._session = session
else:
    session = web.config._session


class index:

    def GET(self):
        return render.index()


class loginUsuario:

    def GET(self):

        # from twython import Twython

        # t = Twython(APP_KEY, APP_SECRET)

        # auth_props = t.get_authentication_tokens(callback_url='http://javonera.dyndns.org:8080/usuario/logincallback')

        # session.oauth_token = auth_props['oauth_token']
        # session.oauth_token_secret = auth_props['oauth_token_secret']

        # web.redirect(auth_props['auth_url'])

        # from twython import Twython

        # session.oauth_token = web.input().oauth_token
        # session.oauth_token_secret = web.input().oauth_token_secret

        # twitter = Twython(APP_KEY, APP_SECRET,
        #             session.oauth_token, session.oauth_token_secret)

        # data = twitter.verify_credentials()
        data = {}
        data['screen_name'] = 'javoBahia'
        session.screen_name = data['screen_name']
        web.debug("antes")
        web.debug(data['screen_name'])
        server_procesador.crear_usuario_en_bd(data['screen_name'])
        web.debug("despues")
#        screen_name_minusculas = data['screen_name'].lower()

#        objetoDB = {}
#        objetoDB["_id"] = screen_name_minusculas

        # import couchdb

        # server = couchdb.Server('http://localhost:5984')

        # try:
        #     db = server.create('usuarios')
        # except couchdb.http.PreconditionFailed:
        #     db = server['usuarios']

        # usuarioEnDB = db.get(screen_name_minusculas)
        # if not usuarioEnDB:
        #     db.save(objtoDB)


        web.redirect('/profile')

class app_login:

    def GET(self):

        return app_render.admin()

class logout:
    def GET(self):
        session.kill()
        web.redirect('/')

class logincallback:

    def GET(self):

        datos_get = web.input()
        oauth_token = datos_get.oauth_token
        oauth_verifier = datos_get.oauth_verifier

        from twython import Twython

        if oauth_token != session.oauth_token:
            web.redirect('/')

        t = Twython(APP_KEY, APP_SECRET,
                    oauth_token, session.oauth_token_secret)

        auth_tokens = t.get_authorized_tokens(oauth_verifier)
        session.auth_tokens = auth_tokens

        # Pasos el nombre a minusculas
        nombre = session.auth_tokens['screen_name'].lower()

        # Guardo en la sesion
        session.screen_name = nombre

        # Uso el nombre como id del objeto en couchDB y lo reemplazo en minusculas
        auth_tokens['_id'] = nombre

        '''Acceso a DB'''

        import couchdb

        server = couchdb.Server('http://localhost:5984')

        try:
            db = server.create('usuarios')
        except couchdb.http.PreconditionFailed:
            db = server['usuarios']

        usuarioEnDB = db.get(nombre)
        if not usuarioEnDB:
            db.save(auth_tokens)

        web.redirect('/usuario/profile')


class profile:
    def GET(self):
        if (not 'screen_name' in session):
            web.redirect('/')
        return usuario_render.profile(session.screen_name)


class app_buscar:
    def GET(self):
        from twython import Twython

        termino = web.input().termino
        usuario = web.input().usuario

        twitter = Twython(APP_KEY, access_token=session.app_access_token)

        resultado = twitter.search(q=termino)

        return app_render.profile(usuario, resultado)


class app_profile:

    def GET(self):

        usuario = web.input().usuario

        session.screen_name = usuario


        return app_render.profile(usuario, '')

class listartweets:
    def GET(self):


        from twitter__util import login
        from twitter__util import imprimirTweets

        try:
            screen_name = session.screen_name
            user_id = session.id
        except:
            web.redirect('/')

        t = login(user_id)
        textos = imprimirTweets(t, user_id)

        return render.frecuencias(screen_name, textos)


class app_listartweets:
    def GET(self):

        from twitter__util import imprimirTweets
        from twitter__util import procesarTweets

        screen_name = web.input().usuario

        textos = imprimirTweets(screen_name)

        procesado = procesarTweets(textos)

        return app_render.profile(screen_name, procesado)

class app_minehometimeline:

    def GET(self):

        from twitter__util import login
        from twitter__util import getHomeTimeline

        screen_name = web.input().usuario

        t = login(screen_name)

        ok = getUserTimeline(screen_name, t)

        url = 'profile?usuario='+screen_name
        web.redirect(url)

        #return app_render.profile(screen_name,'')


class mineusertimeline:

    def GET(self):

        from twitter__util import login
        from twitter__util import getUserTimeline

        screen_name = session.screen_name


        if (not session.auth_tokens):
            t = login(screen_name, 'autorizado')
        else:
            t = login(screen_name)

        ok = getUserTimeline(screen_name, t)

        return usuario_render.profile(screen_name)

class app_mineusertimeline:

    def GET(self):

        from twitter__util import login
        from twitter__util import getUserTimeline

        # t = Twython(APP_KEY, access_token=session.app_access_token)

        screen_name = web.input().usuario

        t = login(screen_name)

        ok = getUserTimeline(screen_name, t)

        url = 'profile?usuario='+screen_name
        web.redirect(url)

        #return app_render.profile(screen_name,'')


class analizarfrecuencia:

    def GET(self):


        from twitter__util import login
        from twitter__util import analisisFrecuencia

        try:
            screen_name = session.screen_name
            user_id = session.id
        except:
            web.redirect('/')

        if (not session.auth_tokens):
            t = login()
        else:
            t = login(user_id)


        import logging
        web.debug('usuario:' + screen_name)
        web.debug('id:' + user_id)

        frecuencias = analisisFrecuencia(t, user_id)

        return render.frecuencias(screen_name, frecuencias)


class app_analizarfrecuencia:

    def GET(self):

        #from twython import Twython

        #twitter = Twython(APP_KEY, access_token=session.app_access_token)

        from twitter__util import analisisFrecuencia

        screen_name = web.input().usuario

        web.debug(screen_name)

        frecuencias = analisisFrecuencia(screen_name)

        return render.frecuencias(screen_name, frecuencias)


class app_conectar:

    def GET(self):

        import socket

        s = socket.socket()
        s.connect(("localhost",  9999))

        mensajeIda = 'anduvo'

        #invoco  el metodo send pasando como parametro el string ingresado por el  usuario
        s.send(mensajeIda)

        mensajeVuelta = s.recv(1024)

        s.close()

        return render.test(mensajeVuelta)

class interaccion_usuario:

    def GET(self, recomendacion):
        recomendacion = 'peliculas'
        usuario = session.screen_name
        resultados = server_procesador.traer_recomendaciones_personalizadas(usuario, recomendacion)        
        return render.recomendacion(resultados, recomendacion)

    def POST(self, funcion):
        if funcion=='aumentar_puntaje':
            peliculaId = web.input().id            
            usuario = session.screen_name
            server_procesador.actualizar_puntaje(peliculaId,usuario, 'aumentar')
            return

        if funcion=='disminuir_puntaje':
            peliculaId = web.input().id            
            usuario = session.screen_name
            server_procesador.actualizar_puntaje(peliculaId, usuario, 'disminuir')
            return


class utilidades:

    def GET(self, funcion):
        if funcion=="reentrenar_clasificador":
            server_clasificador.entrenar_clasificador()
            return "Clasificador entrenado"

        if funcion=="conectar_twitter":
            server_procesador.conectar_a_twitter()
            return "Conectado a twitter"

        if funcion=="mostrar_tweets":
            campos = [("Tweet")]
            return render.tabla(campos+server_almacenador.get_tweets())

        if funcion=="clasificar_tweets":
            return  server_clasificador.analizar_sentimientos()

        if funcion=="mostrar_tweets_clasificados":
            campos = [("Tweet", "Palabras", "Clasificacion", "Certeza")]
            tweetsClasificados = server_almacenador.get_tweets_clasificados()
            return render.tabla(campos + tweetsClasificados)

        if funcion=="obtener_nes":
            return server_procesador.obtener_nes()

        if funcion=="mostrar_nes":
            campos = [("Tweet", "Palabras", "NEs")]
            return render.tabla(campos + server_almacenador.get_nes())

        if funcion=="obtener_sugerencias":
            return server_procesador.obtener_sugerencias()

        if funcion=="mostrar_sugerencias":
            tipoTweets = server_almacenador.get_tipo_tweets()
            sugerencias = server_almacenador.get_sugerencias()
            web.debug(sugerencias)
            return render.sugerencias(tipoTweets, sugerencias)

        if funcion=="guardar_sugerencias":
            return server_procesador.guardar_recomendaciones_en_bd("peliculas")
        return

    def POST(self, funcion):

        if funcion=="clasificar_tweets_entrenamiento":
            #categorias=sorted(web.input().categorias.split(','))
            categorias=web.input().categorias.split(',')
            tweets = server_almacenador.get_tweets()
            return render.clasificar(tweets, categorias)

        if funcion=="obtener_tweets":
            termino = web.input().termino
            tipoTweet = web.input().tipoTweets
            web.debug(tipoTweet)
            return server_procesador.obtener_tweets(termino, tipoTweet)

        if funcion=="guardar_tweets_entrenamiento":
            tweets_entrenamiento = json.loads(web.input().entrenamiento)
            archivo = web.input().archivo
            web.debug(tweets_entrenamiento)
            web.debug(archivo)
            server_clasificador.editar_archivo_entrenamiento(archivo, tweets_entrenamiento)
            return "oka"

class app_entrenamiento:

    def POST(self):
        archivo=web.input().archivo
        web.debug(archivo)
        categorias = server_procesador.obtenerCategoriasArchivo(archivo)
        return app_render.entrenamiento(categorias, archivo)



class app_sugerencias_peliculas:

    def GET(self):

        '''
        clasificador = entrenar_clasificador()
        tweets_recientes = obtener_tweets_recientes()
        tweets_clasificados = clasificar_tweets(clasificador, tweets_recientes)
        lista_ne = obtener_ne(tweets_clasificados)
        sugerencias = obtener_peliculas_desde_ne(lista_ne)
        '''

        from funciones import *
        clasificador, word_features = entrenarClasificador()
        cuenta = conexion()        
        tweetsPedidos = pedirTweetsPeliculas(cuenta)
        tweetsBienClasificados = clasificarTweets(clasificador, tweetsPedidos, word_features)
        listaNEs = obtenerNEs(tweetsBienClasificados)
        listaFinal = obtenerPeliculas(listaNEs)

        return app_render.sugerenciasPeliculas(listaFinal)
     
class app_sugerencias_musica:

    def GET(self):


        return app_render.sugerenciasDiscos(listaFinal)


if __name__ == "__main__":
    app.run()
