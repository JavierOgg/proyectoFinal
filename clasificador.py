# saved as greeting.py

import Pyro4
import sys


from funciones import entrenarClasificador
from funciones import clasificarTweets

server_almacenador = Pyro4.Proxy("PYRONAME:quehago.almacenador")    # use name server object lookup uri shortcut

Pyro4.config.ONEWAY_THREADED = True

tipoClasificador = sys.argv[1]

class Clasificador(object):

    def __init__(self):
        #self.entrenar_clasificador()
        return

    def entrenar_clasificador(self, archivo='default'):
        if archivo == "default":
            if tipoClasificador == "sentimientos":
                archivo = "sentiment2.csv"
            else:
                archivo = "categorias.csv"
        self.clasificador, self.word_features, self.sentimientos = entrenarClasificador(archivo)
        return

    def editar_archivo_entrenamiento(self, nombre_archivo, tweets):
        import csv
        from sets import Set
        tweetsExistentes = Set()
        try:
            fp = open(nombre_archivo, 'rb')
            reader = csv.reader(fp, delimiter=',', quotechar='"', escapechar='\\')

            for row in reader:
                tweetsExistentes.add(row[0])

            fp.close()

            fp = open(nombre_archivo, 'ab')
        except:
            fp = open(nombre_archivo, 'wb')
        writer = csv.writer(fp, delimiter=',', quotechar='"', escapechar='\\', quoting=1)
        print tweetsExistentes
        for tweet in tweets:
            if tweet['id'] not in tweetsExistentes:
                writer.writerow([tweet['id'], tweet['clasificacion'], tweet['tweet'].encode("utf-8")])
        fp.close()
        return "ok"

    def clasificar_tweets(self, tweets):
        tweetsClasificados = clasificarTweets(self.clasificador, tweets, self.word_features, self.sentimientos)
        server_almacenador.set_tweets_clasificados(tweetsClasificados)
        return tweetsClasificados

    def analizar_sentimientos(self):
        try:
            tweets = server_almacenador.get_tweets()
            tweetsClasificados = clasificarTweets(self.clasificador, tweets, self.word_features, self.sentimientos)
            server_almacenador.set_tweets_clasificados(tweetsClasificados)
            return "Tweets clasificados"
        except NameError:
            return "Antes de ejecutar esta funcion debe llamar a entrenar_clasificador"

    def get_word_features(self):
        return self.word_features

servidor_clasificador = Clasificador()

daemon = Pyro4.Daemon()                 # make a Pyro daemon
ns = Pyro4.locateNS()                   # find the name server
uri = daemon.register(servidor_clasificador)   # register the greeting object as a Pyro object
ns.register("quehago.clasificador."+tipoClasificador, uri)  # register the object with a name in the name server

print 'Ready.'
daemon.requestLoop()                  # start the event loop of the server to wait for calls
