# saved as greeting.py

import Pyro4

class Almacenador(object):

    def status(self):
        
        return

    def get_tweets(self):
        return self.tweets

    def get_tweets_clasificados(self):
        return self.tweetsClasificados

    def get_nes(self):
        return self.nes

    def get_sugerencias(self):
        return self.sugerencias

    def get_tipo_tweets(self):
        return self.tipoTweets

    def set_tweets(self, tweets):
        self.tweets = tweets
        print "Tweets guardados"
        return 

    def set_tweets_clasificados(self, tweetsClasificados):
        self.tweetsClasificados = tweetsClasificados
        print "Tweets clasificados guardados"
        return

    def set_nes(self, nes):
        self.nes = nes
        print "NEs guardados"
        return

    def set_sugerencias(self, sugerencias):
        self.sugerencias = sugerencias
        print "Sugerencias guardadas"
        return

    def set_tipo_tweets(self, tipoTweets):
        self.tipoTweets = tipoTweets
        print "Tipo tweets guardados"
        return


servidor_almacenador=Almacenador()

daemon=Pyro4.Daemon()                 # make a Pyro daemon
ns=Pyro4.locateNS()                   # find the name server
uri=daemon.register(servidor_almacenador)   # register the greeting object as a Pyro object
ns.register("quehago.almacenador", uri)  # register the object with a name in the name server

print 'Ready.'
daemon.requestLoop()                  # start the event loop of the server to wait for calls
