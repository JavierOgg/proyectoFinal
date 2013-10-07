import web
import json
import Pyro4

server_clasificador_sentimientos = Pyro4.Proxy("PYRONAME:quehago.clasificador.sentimientos")    # use name server object lookup uri shortcut
server_clasificador_categorias = Pyro4.Proxy("PYRONAME:quehago.clasificador.categorias")    # use name server object lookup uri shortcut
server_procesador = Pyro4.Proxy("PYRONAME:quehago.procesador")    # use name server object lookup uri shortcut
server_procesador._pyroOneway.add("actualizar_timeline")
server_almacenador = Pyro4.Proxy("PYRONAME:quehago.almacenador")    # use name server object lookup uri shortcut


def imprimirlindo(texto):
    return json.dumps(texto, sort_keys=True, indent=4)

# render = web.template.render('templates/', globals={'imprimir':imprimirlindo})
render = web.template.render('templates/', globals={'imprimir': imprimirlindo, 'tipo': isinstance})
#app_render = web.template.render('templates/app', globals={'imprimir':imprimirlindo})
#usuario_render = web.template.render('templates/usuario')

urls = (
    '/', 'index',
    '/login', 'login',
    '/profile', 'profile',
    '/admin', 'admin',
    '/test', 'test',
    '/admin/utilidades/(.*)', 'utilidades',
    '/entrenamiento', 'entrenamiento',
    '/clasificacion', 'clasificacion',
    '/interaccion_usuario/(.*)', 'interaccion_usuario',
    '/logout', 'logout'
)

app = web.application(urls, globals())

if web.config.get('_session') is None:
    session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={
        'screen_name': '',
        'oauth_token': '',
        'oauth_token_secret': ''
    })
    web.config._session = session
else:
    session = web.config._session


class index:
    def GET(self):
        return render.index()


class login:
    def GET(self):
        if session['screen_name'] == '':
            APP_KEY = 'oyEys6d4bYh3VVMHE8cvAw'
            APP_SECRET = 'wqHM5ZuDOQwRmD1VzBjLxHH6pKu9FAfo1gPp7nUSKc4'

            print "no hay sesion"

            from twython import Twython

            session.oauth_token = web.input().oauth_token
            session.oauth_token_secret = web.input().oauth_token_secret

            twitter = Twython(APP_KEY, APP_SECRET, session.oauth_token, session.oauth_token_secret)

            data = twitter.verify_credentials()

            session.screen_name = data['screen_name']

        server_procesador.crear_usuario_en_bd(session.screen_name, session.oauth_token, session.oauth_token_secret)

        server_procesador.actualizar_timeline(session.screen_name)

        web.redirect('/profile')


class admin:
    def GET(self):
        return render.admin()


class clasificacion:
    def GET(self):
        return render.clasificacion()


class entrenamiento:
    def GET(self):
        return render.entrenamiento('', '')

    def POST(self):
        archivo = web.input().archivo
        categorias = server_procesador.obtenerCategoriasArchivo(archivo)
        return render.entrenamiento(categorias, archivo)


class logout:
    def GET(self):
        session.kill()
        web.redirect('/')


class profile:
    def GET(self):
        if (not 'screen_name' in session):
            web.redirect('/')
        return render.profile(session.screen_name)


class interaccion_usuario:

    def GET(self, recomendacion):
        usuario = session.screen_name
        resultados = server_procesador.traer_recomendaciones_personalizadas(usuario, recomendacion)
        if recomendacion == 'peliculas':
            return render.recomendacionPeliculas(resultados)
        if recomendacion == 'musica':
            return render.recomendacionMusica(resultados)

    def POST(self, funcion):
        if funcion == 'aumentar_puntaje':
            peliculaId = web.input().id
            usuario = session.screen_name
            server_procesador.actualizar_puntaje(peliculaId, usuario, 'aumentar')
            return

        if funcion == 'disminuir_puntaje':
            peliculaId = web.input().id
            usuario = session.screen_name
            server_procesador.actualizar_puntaje(peliculaId, usuario, 'disminuir')
            return


class utilidades:

    def GET(self, funcion):
        if funcion == "conectar_twitter":
            server_procesador.conectar_a_twitter()
            return "Conectado a twitter"

        if funcion == "mostrar_tweets":
            campos = [("Tweet")]
            return render.tabla(campos+server_almacenador.get_tweets())

        if funcion == "clasificar_tweets":
            return server_clasificador_sentimientos.analizar_sentimientos()

        if funcion == "mostrar_tweets_clasificados":
            campos = [("Tweet", "Palabras", "Clasificacion", "Certeza")]
            tweetsClasificados = server_almacenador.get_tweets_clasificados()
            return render.tabla(campos + tweetsClasificados)

        if funcion == "obtener_nes":
            return server_procesador.obtener_nes()

        if funcion == "mostrar_nes":
            campos = [("Tweet", "Palabras", "NEs")]
            return render.tabla(campos + server_almacenador.get_nes())

        if funcion == "obtener_sugerencias":
            return server_procesador.obtener_sugerencias()

        if funcion == "mostrar_sugerencias":
            tipoTweets = server_almacenador.get_tipo_tweets()
            sugerencias = server_almacenador.get_sugerencias()
            web.debug(sugerencias)
            return render.sugerencias(tipoTweets, sugerencias)

        if funcion == "guardar_sugerencias":
            return server_procesador.guardar_recomendaciones_en_bd()
        return

    def POST(self, funcion):

        if funcion == "reentrenar_clasificador":
            return server_clasificador_sentimientos.entrenar_clasificador()

        if funcion == "reentrenar_clasificador_archivo":
            archivo = web.input().archivo
            return server_clasificador_sentimientos.entrenar_clasificador(archivo)

        if funcion == "clasificar_tweets_entrenamiento":
            categorias = web.input().categorias.split(',')
            termino = web.input().termino

            tweets = server_procesador.obtener_tweets(termino, 'entrenamiento')
            return render.clasificar(tweets, categorias)

        if funcion == "obtener_tweets":
            termino = web.input().termino
            tipoTweet = web.input().tipoTweets
            return server_procesador.obtener_tweets(termino, tipoTweet)

        if funcion == "guardar_tweets_entrenamiento":
            tweets_entrenamiento = json.loads(web.input().entrenamiento)
            archivo = web.input().archivo

            server_clasificador_sentimientos.editar_archivo_entrenamiento(archivo, tweets_entrenamiento)
            return "oka"



if __name__ == "__main__":
    app.run()
