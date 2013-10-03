from __future__ import division
from types import *
import json
import csv
import nltk
import re
import httplib
import datetime
import web
from time import sleep
from sets import Set

stopwords = nltk.corpus.stopwords.words('english')+['-', 'rt']


def entrenarClasificador(archivo):
    def extract_features(document):
        document_words = set(document)
        features = {}
        for word in word_features:
            features['contains(%s)' % word] = (word in document_words)
        return features

    tweets = []
    sentimientos = Set()

    # Poner un try/except
    fp = open(archivo, 'rb')
    reader = csv.reader(fp, delimiter=',', quotechar='"', escapechar='\\')

    for row in reader:
        tweets.append([row[2], row[1]])
        sentimientos.add(row[1])

    tweetsMinimizados = []

    for (words, sentiment) in tweets:
        listaPalabras = minimizar_y_quitarStopwords(words)
        tweetsMinimizados.append((listaPalabras, sentiment))

        training_tweets = tweetsMinimizados

    word_features = get_word_features(get_words_in_tweets(training_tweets))

    training_set = nltk.classify.apply_features(extract_features, training_tweets)

    classifier = nltk.NaiveBayesClassifier.train(training_set)

    return classifier, word_features, list(sentimientos)


def clasificarTweets(clasificador, tweets, word_features, sentimientos):

    def extract_features(document):
        document_words = set(document)
        features = {}
        for word in word_features:
            features['contains(%s)' % word] = (word in document_words)
        return features

    testing_tweets = []
    for tweet in tweets:
        listaPalabras = minimizar_y_quitarStopwords(tweet)
        testing_tweets.append(listaPalabras)
    test_featuresets = [extract_features(n) for n in testing_tweets]

    tweetsTextos = tweets

    pdists = clasificador.batch_prob_classify(test_featuresets)

    resultados = []
    for (listaPalabras, pdist, tweet) in zip(testing_tweets, pdists, tweetsTextos):
        lista = [pdist.prob(s) for s in sentimientos]
        maximo = max(lista)
        clasificacion = sentimientos[lista.index(maximo)]
        lista.remove(maximo)
        segundo = max(lista)
        diferencia = maximo-segundo
        if diferencia > 0.5:
            resultados.append((tweet, listaPalabras, clasificacion, diferencia))

    listaNueva = sorted(resultados, key=lambda tweet: tweet[3], reverse=True)

    return listaNueva


def obtenerNEs(lista):

    listaGeneral = []

    for (tweet, listaPalabras, clasificacion, diferenciaProbabilidad) in lista:
        # Condicionamos para que solo evalue los positivos
        print clasificacion
        if clasificacion == 'positive':
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

            if listaNEs:
                listaGeneral.append((tweet, listaPalabras, listaNEs))

    web.debug('Tweets con NEs:' + str(len(listaGeneral)))
    return listaGeneral


def minimizar_y_quitarStopwords(tweet):
    tweetLowercase = tweet.lower()
    listaPalabras = tweetLowercase.split()
    listaPalabras = quitarExcedente(listaPalabras)
    return listaPalabras


def obtenerPeliculas(lista):
    def cumpleCondicionesMinimas(jsonPelicula, listaPalabras):
        if not 'poster' in jsonPelicula:
            return False
        titulo = jsonPelicula['title']
        listaPalabrasTitulo = titulo.lower().split()
        listaPalabrasTituloSinStopwords = [palabra for palabra in listaPalabrasTitulo if palabra not in stopwords]
        cantidadPalabrasTitulo = len(listaPalabrasTituloSinStopwords)

        cant = 0
        for palabra in listaPalabrasTituloSinStopwords:
            if palabra in listaPalabras:
                cant = cant + 1

        return cant == cantidadPalabrasTitulo

    conn = httplib.HTTPConnection("mymovieapi.com")
    url = "/?title=%s&type=json&plot=simple&episode=0&limit=3&yg=0&mt=M&lang=en-US&offset=&aka=simple&release=simple&business=0&tech=0&exact=true"

    cantidadPedidos = 0
    listaFinal = []
    for (tweet, listaPalabras, listaNE) in lista:
        listaPeliculas = []

        for ne in listaNE:

            pelicula = '+'.join(ne)
            sleep(2)
            conn.request("GET", url % pelicula)
            cantidadPedidos += 1
            r1 = conn.getresponse()
            if r1.reason == "OK":
                peliculas = json.loads(r1.read().encode('utf-8'))
                if isinstance(peliculas, list):
                    for pelicula in peliculas:
                        if cumpleCondicionesMinimas(pelicula, listaPalabras):
                            listaPeliculas.append(pelicula)
                            break
            else:
                web.debug("Error pedido: "+str(r1.reason))
        if listaPeliculas:
            listaFinal.append((tweet, listaNE, listaPeliculas))
    conn.close()

    web.debug("Pedidos totales: "+str(cantidadPedidos))
    web.debug('Tweets con peliculas:' + str(len(listaFinal)))
    return listaFinal


def obtenerDiscos(lista):
    def cumpleCondicionesMinimasDiscos(jsonDisco, tweet):
        tweet = tweet.lower()
        titulo = jsonDisco['name'].lower()

        if not titulo in tweet:
            return False
        web.debug("titulo: "+titulo)

        artista = jsonDisco['artist'].lower()
        web.debug("artista: "+artista)
        if artista == titulo:
            longitud = len([m.start() for m in re.finditer(artista, tweet)])
            if longitud > 1:
                return True
            else:
                return False
        if artista in tweet:
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

        for ne in listaNE:

            disc = '+'.join(ne)
            conn.request("GET", url % disc)
            cantidadPedidos += 1
            r1 = conn.getresponse()
            if r1.reason == "OK":
                #jsonDiscos = json.loads(r1.read().encode('utf-8'))
                jsonDiscos = json.loads(r1.read())
                try:
                    jsonListaDiscos = jsonDiscos["results"]["albummatches"]["album"]
                    for disco in jsonListaDiscos:
                        print disco
                        if cumpleCondicionesMinimasDiscos(disco, tweet):
                            if not disco in listaDiscos:
                                listaDiscos.append(disco)
                            break
                except:
                    web.debug("No hay matches de discos")
            else:
                web.debug("Error pedido: "+str(r1.reason))
        if listaDiscos:
            listaFinal.append((tweet, listaNE, listaDiscos))
    conn.close()

    web.debug("Pedidos totales: "+str(cantidadPedidos))
    web.debug('Tweets con Musica:' + str(len(listaFinal)))
    return listaFinal


def quitarExcedente(tweet):
    # Sacamos stopswords, y hacemos split de los tweets

    lista = [palabra for palabra in tweet if palabra not in stopwords
             and not re.match('^\#|@', palabra) and
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
        if t.node == 'NE':
            subLista = []
            for child in t:
                traverse(child, subLista, True)
            lista.append(subLista)
        else:
            for child in t:
                traverse(child, lista, False)
