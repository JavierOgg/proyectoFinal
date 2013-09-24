from __future__ import division
from twython import Twython
from types import *
import json
import csv
import nltk, re
import httplib
import datetime
import web
from time import sleep

stopwords = nltk.corpus.stopwords.words('english')+['-','rt']

def entrenarClasificador():
    web.debug('Inicio Entrenar Clasificador')
    def extract_features(document):
        document_words = set(document)
        features = {}
        for word in word_features:
            features['contains(%s)' % word] = (word in document_words)
        return features

    # read all tweets and labels
    fp = open( 'sentiment.csv', 'rb' )
    reader = csv.reader( fp, delimiter=',', quotechar='"', escapechar='\\' )
    tweets = []
    contador = 0
    for row in reader:
        if (row[1]!="neutral" and row[1]!="irrelevant"):
            tweets.append( [row[4], row[1]] );
        else:
            contador = contador + 1
            if (contador==5):
                tweets.append( [row[4], row[1]] )
                contador=0

    # treat neutral and irrelevant the same
    for t in tweets:
        if t[1] == 'irrelevant':
            t[1] = 'neutral'

    #random.shuffle( tweets );

    tweetsMinimizados = []
    paresTweets = []

    for (words, sentiment) in tweets:
        tweetLowercase = words.lower()
        listaPalabras = tweetLowercase.split()
        listaPalabras = quitarExcedente(listaPalabras)

        tweetsMinimizados.append((listaPalabras, sentiment))
        paresTweets.append((listaPalabras, words, sentiment))

        #totalTweets = len(tweets)
        #division = int(totalTweets*0.9)
        training_tweets = tweetsMinimizados
        #testing_tweets = tweetsMinimizados[division:]


    word_features = get_word_features(get_words_in_tweets(training_tweets))
    web.debug('Tweets de entrenamiento: '+str(len(tweetsMinimizados)))

    training_set = nltk.classify.apply_features(extract_features, training_tweets)
    #testing_set = nltk.classify.apply_features(extract_features, testing_tweets)

    classifier = nltk.NaiveBayesClassifier.train(training_set)

    #retorna el clasificador
    return classifier, word_features

# Obtenemos acceso a Twitter
'''
def conexion():
    web.debug('Inicio Conexions:' + str(datetime.datetime.now()))
    APP_KEY = '4EDYH92aDYG06Mak7xg'
    APP_SECRET = 'KBNlPuQl0xaTgzbzbMydJXm56fvlPCvEe054pLcmEnc'

    twitter = Twython(APP_KEY, APP_SECRET, oauth_version=2)
    ACCESS_TOKEN = twitter.obtain_access_token()
    twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)
    return twitter


# Pedimos tweets con una consulta particular
def pedirTweetsPeliculas(twitter):
    web.debug('Inicio Pedir tweets:' + str(datetime.datetime.now()))
    #results = twitter.search(q='excellent movie', lang='en', count=100, result_type="popular")
    results = twitter.search(q=' movie', lang='en', count=100)

    # Hacemos una busqueda
    statuses = results['statuses']
    tweetsNuevos = []
    for status in statuses:
        if not 'RT @' in status['text']:
            tweetsNuevos.append(status['text'].encode('utf-8'))

    web.debug('Tweets obtenidos:' + str(len(tweetsNuevos)))

    return tweetsNuevos

def pedirTweetsDiscos(twitter):
    web.debug('Inicio Pedir tweets:' + str(datetime.datetime.now()))
    #results = twitter.search(q='excellent movie', lang='en', count=100, result_type="popular")
    results = twitter.search(q='great album', lang='en', count=100)

    # Hacemos una busqueda
    statuses = results['statuses']
    tweetsNuevos = []
    for status in statuses:
        if not 'RT @' in status['text']:
            tweetsNuevos.append(status['text'].encode('utf-8'))

    web.debug('Tweets obtenidos:' + str(len(tweetsNuevos)))

    return tweetsNuevos

'''    

def clasificarTweets(clasificador, tweets, word_features):

    def extract_features(document):
        document_words = set(document)
        features = {}
        for word in word_features:
            features['contains(%s)' % word] = (word in document_words)
        return features

    # Sacamos stopwords, y hacemos split de los tweets
    def procesarTweetsPlanos(tweet):
        tweetLowercase = tweet.lower()
        listaPalabras = tweetLowercase.split()
        listaPalabras = quitarExcedente(listaPalabras)
        return listaPalabras


    web.debug('Inicio clasificar tweets:' + str(datetime.datetime.now()))

    testing_tweets = []
    for tweet in tweets:
        listaPalabras = procesarTweetsPlanos(tweet)
        testing_tweets.append(listaPalabras)
    test_featuresets = [extract_features(n) for n in testing_tweets]

    tweetsTextos = tweets

    pdists = clasificador.batch_prob_classify(test_featuresets)

    resultados = []
    for (listaPalabras, pdist, tweet) in zip(testing_tweets, pdists, tweetsTextos):
        lista = [pdist.prob('positive'), pdist.prob('neutral'), pdist.prob('negative')]
        maximo = max(lista)
        lista.remove(maximo)
        segundo = max(lista)
        diferencia = maximo-segundo
        resultados.append((tweet, listaPalabras,clasificador.classify(extract_features(listaPalabras)), diferencia))


    listaNueva = sorted(resultados, key=lambda tweet: tweet[3], reverse=True)
    listaAcotada = [tweet for tweet in listaNueva if tweet[3] > 0.5 ]

    '''
    for elem  in listaNueva:
        web.debug(elem)
    '''

    web.debug('Tweets acotados:' + str(len(listaAcotada)))

    return listaAcotada

def obtenerNEs(lista):

    listaGeneral = []

    for (tweet, listaPalabras, clasificacion, diferenciaProbabilidad) in lista:
        sentences = nltk.tokenize.sent_tokenize(tweet)
        # Hacemos split en lugar de tokenize, para poder extrar las menciones a usuario.
        # El word_tokenize, separa el @ entonces no podemos filtrar
        nuevaSentences = []
        for s in sentences:
            subLista = quitarExcedenteSimple(s.split())
            nuevaSentences.append(' '.join(subLista))


        tokens = [nltk.tokenize.word_tokenize(s) for s in nuevaSentences]

        pos_tagged_tokens = [nltk.pos_tag(t) for t in tokens]
        ne_chunks = nltk.batch_ne_chunk(pos_tagged_tokens, binary=True)

        listaNEs = []
        for subArbol in ne_chunks:
            traverse(subArbol, listaNEs, False)


        if len(listaNEs)>0:
            listaGeneral.append((tweet, listaPalabras, listaNEs))

    web.debug('Tweets con NEs:' + str(len(listaGeneral)))
    return listaGeneral

def obtenerPeliculas(lista):    
    def cumpleCondicionesMinimas(jsonPelicula, listaPalabras):        
        if not 'poster' in jsonPelicula:
            return False
        titulo = jsonPelicula['title']
        listaPalabrasTitulo = titulo.lower().split()
        listaPalabrasTituloSinStopwords = [palabra for palabra in listaPalabrasTitulo if palabra not in stopwords]
        cantidadPalabrasTitulo = len(listaPalabrasTituloSinStopwords)
        #listaNEs_min = [palabra.lower() for palabra in listaNEs]
        cant = 0    
        for palabra in listaPalabrasTituloSinStopwords:
            if palabra in listaPalabras:
                cant = cant + 1
        #porcentaje = cant / cantidadPalabrasTitulo
        # web.debug("Palabras Tweet: "+str(listaPalabras))
        # web.debug("Palabras Titulo: "+str(listaPalabrasTituloSinStopwords))
        # web.debug("")
        return cant == cantidadPalabrasTitulo
        
    web.debug('Inicio obtener peliculas:' + str(datetime.datetime.now()))
    conn = httplib.HTTPConnection("mymovieapi.com")
    url = "/?title=%s&type=json&plot=simple&episode=0&limit=3&yg=0&mt=M&lang=en-US&offset=&aka=simple&release=simple&business=0&tech=0&exact=true"

    cantidadPedidos = 0
    listaFinal = []
    for (tweet, listaPalabras, listaNE) in lista:
        listaPeliculas = []
        # web.debug("Tweet: "+tweet)
        for ne in listaNE:
            # web.debug("NEs: "+str(ne))
            pelicula = '+'.join(ne)
            sleep(2)
            conn.request("GET", url % pelicula)
            cantidadPedidos += 1
            r1 = conn.getresponse()
            if r1.reason=="OK":
                peliculas = json.loads(r1.read().encode('utf-8'))
                if type(peliculas) is list:
                    for pelicula in peliculas:
                        if cumpleCondicionesMinimas(pelicula, listaPalabras):
                            listaPeliculas.append(pelicula)
                            break
            else:
                web.debug("Error pedido: "+str(r1.reason))
        if len(listaPeliculas) > 0:
            listaFinal.append((tweet, listaNE, listaPeliculas))
    conn.close()

    web.debug("Pedidos totales: "+str(cantidadPedidos))
    web.debug('Tweets con peliculas:' + str(len(listaFinal)))
    return listaFinal


def obtenerDiscos(lista):    
    def cumpleCondicionesMinimasDiscos(jsonDisco, tweet):        
        tweet = tweet.lower()
        titulo = jsonDisco['name'].lower()
        #listaPalabrasTitulo = titulo.lower().split()
        #listaPalabrasTituloSinStopwords = [palabra for palabra in listaPalabrasTitulo if palabra not in stopwords]
        #cantidadPalabrasTitulo = len(listaPalabrasTituloSinStopwords)

        if not titulo in tweet:
            return False
        web.debug("titulo: "+titulo)

        '''
        cant = 0    
        for palabra in listaPalabrasTituloSinStopwords:
            if palabra in listaPalabras:
                cant = cant + 1

        if cant == 0:
            return False

        if cant != cantidadPalabrasTitulo:
            return False

        artista = jsonDisco['artist']
        listaPalabrasArtista = artista.lower().split()
        listaPalabrasArtistaSinStopwords = [palabra for palabra in listaPalabrasArtista if palabra not in stopwords]
        cantidadPalabrasArtista = len(listaPalabrasArtistaSinStopwords)

        cant = 0    
        for palabra in listaPalabrasArtistaSinStopwords:
            if palabra in listaPalabras:
                cant = cant + 1

        return cant>0 and cant == cantidadPalabrasArtista
        '''

        artista = jsonDisco['artist'].lower()
        web.debug("artista: "+artista)        
        if artista == titulo:
            longitud = len([m.start() for m in re.finditer(artista, tweet)])
            if longitud >1:
                web.debug("------- HAY MATCH -----")
                return True
            else:
                return False
        if artista in tweet:
            web.debug("------- HAY MATCH -----")
            return True
        else:
            return False


        
    web.debug('Inicio obtener discos:' + str(datetime.datetime.now()))
    conn = httplib.HTTPConnection("ws.audioscrobbler.com")

    url = "/2.0/?method=album.search&album=%s&api_key=958e5ca979db8f118d61d48927815ea5&format=json"

    cantidadPedidos = 0
    listaFinal = []
    for (tweet, listaPalabras, listaNE) in lista:
        listaDiscos = []
        web.debug("Tweet: "+tweet)
        for ne in listaNE:
            web.debug("NEs: "+str(ne))
            disc = '+'.join(ne)
            conn.request("GET", url % disc)
            cantidadPedidos += 1
            r1 = conn.getresponse()
            if r1.reason=="OK":
                jsonDiscos = json.loads(r1.read().encode('utf-8'))
                try: 
                    jsonListaDiscos = jsonDiscos["results"]["albummatches"]["album"]
                    for disco in jsonListaDiscos:
                        if cumpleCondicionesMinimasDiscos(disco, tweet):
                            if not disco in listaDiscos:
                                listaDiscos.append(disco)
                            break
                except:
                    web.debug("No hay matches de discos")
            else:
                web.debug("Error pedido: "+str(r1.reason))
        if len(listaDiscos) > 0:
            listaFinal.append((tweet, listaNE, listaDiscos))
    conn.close()

    web.debug("Pedidos totales: "+str(cantidadPedidos))
    web.debug('Tweets con Musica:' + str(len(listaFinal)))
    return listaFinal

def quitarExcedente(tweet):
    # Sacamos stopswords, y hacemos split de los tweets
    

    lista = [palabra for palabra in tweet if palabra not in stopwords and
                            not re.match('^\#|@', palabra) and
                            not re.match('^http', palabra)
                            ]
    nuevaLista = []
    for w in lista:
        nuevaLista.append(re.sub('[.!,:;\"\?]', '', w))
    return nuevaLista

def quitarExcedenteSimple(tweet):
    lista = [palabra for palabra in tweet if not re.match('^\#|@', palabra) and not re.match('^http', palabra)]
    return lista


# Junta todas las palabras en una lista
def get_words_in_tweets(tweets):
    all_words = []
    for (words, sentiment) in tweets:
      all_words.extend(words)
    return all_words


def get_word_features(wordlist):
    wordlist = nltk.FreqDist(wordlist)
    word_features = wordlist.keys()
    return word_features






def traverse(t, lista, agregar):
    try:
        t.node
    except AttributeError:
        if agregar:
            lista.append(t[0])
    else:
        if t.node=='NE':
            subLista = []
            for child in t:
                traverse(child, subLista, True)
            lista.append(subLista)
        else:
            for child in t:
                traverse(child, lista, False)



