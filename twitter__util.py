# -*- coding: utf-8 -*-
import web
import sys
import locale
import twitter
# import redis
import json
import time
import logging
from random import shuffle
from urllib2 import URLError


def login(screen_name, estado = 'desautorizado' ):

    # Go to http://twitter.com/apps/new to create an app and get these items
    # See also http://dev.twitter.com/pages/oauth_single_token

    CONSUMER_KEY = 'oyEys6d4bYh3VVMHE8cvAw'
    CONSUMER_SECRET = 'wqHM5ZuDOQwRmD1VzBjLxHH6pKu9FAfo1gPp7nUSKc4'

    # VERIFICAR QUE SE EJECUTA EL ELSE SI EL PARAMETRO ES 0
    if estado == 'autorizado':
        import couchdb
        server = couchdb.Server('http://localhost:5984')
        db = server['usuarios']
        usuario = db.get(screen_name)

        oauth_token = usuario['oauth_token']
        oauth_token_secret = usuario['oauth_token_secret']

    else:  # Me loguo como la app (en realidad me logueo como javoBahia, son mis tokens los que aparecen en dev.tweeter.com)
        oauth_token = '190536889-zMkjzjUBHdZ48MMCd1rMtN5xZVZAw5ER26oqhy5k'
        oauth_token_secret = '50g1USgyl3t1NuMgYM6Nv5Ro6tmKH47EGVSY5DOLQg'


    return twitter.Twitter(domain='api.twitter.com', api_version='1.1',
                           auth=twitter.oauth.OAuth(
                           oauth_token, oauth_token_secret,
                           CONSUMER_KEY, CONSUMER_SECRET))


def makeTwitterRequest(t, twitterFunction, max_errors=3, *args, **kwArgs):
    wait_period = 2
    error_count = 0
    while True:
        try:
            return twitterFunction(*args, **kwArgs)
        except twitter.api.TwitterHTTPError, e:
            error_count = 0
            wait_period = handleTwitterHTTPError(e, t, wait_period)
            if wait_period is None:
                return
        except URLError, e:
            error_count += 1
            print >> sys.stderr, "URLError encountered. Continuing."
            if error_count > max_errors:
                print >> sys.stderr, "Too many consecutive errors...bailing out."
                raise


def _getRemainingHits(t):
    return t.account.rate_limit_status()['remaining_hits']


# Handle the common HTTPErrors. Return an updated value for wait_period
# if the problem is a 503 error. Block until the rate limit is reset if
# a rate limiting issue
def handleTwitterHTTPError(e, t, wait_period=2):

    if wait_period > 3600:  # Seconds
        print >> sys.stderr, 'Too many retries. Quitting.'
        raise e

    if e.e.code == 401:
        print >> sys.stderr, 'Encountered 401 Error (Not Authorized)'
        return None
    elif e.e.code in (502, 503):
        print >> sys.stderr, 'Encountered %i Error. Will retry in %i seconds' % (
            e.e.code, wait_period)
        time.sleep(wait_period)
        wait_period *= 1.5
        return wait_period
    elif _getRemainingHits(t) == 0:
        status = t.account.rate_limit_status()
        now = time.time()  # UTC
        when_rate_limit_resets = status['reset_time_in_seconds']  # UTC
        sleep_time = max(
            when_rate_limit_resets - now, 5)  # Prevent negative numbers
        print >> sys.stderr, 'Rate limit reached: sleeping for %i secs' % (
            sleep_time, )
        time.sleep(sleep_time)
        return 2
    else:
        raise e


# A template-like function that can get friends or followers depending on
# the function passed into it via func.

def _getFriendsOrFollowersUsingFunc(
    func,
    key_name,
    t,  # Twitter connection
    r,  # Redis connection
    screen_name=None,
    limit=10000,
):

    cursor = -1

    result = []
    while cursor != 0:
        response = makeTwitterRequest(
            t, func, screen_name=screen_name, cursor=cursor)
        for _id in response['ids']:
            result.append(_id)
            r.sadd(getRedisIdByScreenName(screen_name, key_name), _id)

        cursor = response['next_cursor']
        scard = r.scard(getRedisIdByScreenName(screen_name, key_name))
        print >> sys.stderr, 'Fetched %s ids for %s' % (scard, screen_name)
        if scard >= limit:
            break

    return result


def getUserInfo(
    t,  # Twitter connection
    r,  # Redis connection
    screen_names=[],
    user_ids=[],
    verbose=False,
    sample=1.0,
):

    # Sampling technique: randomize the lists and trim the length.

    if sample < 1.0:
        for lst in [screen_names, user_ids]:
            shuffle(lst)
            lst = lst[:int(len(lst) * sample)]

    info = []
    while len(screen_names) > 0:
        screen_names_str = ','.join(screen_names[:100])
        screen_names = screen_names[100:]

        response = makeTwitterRequest(t,
                                      t.users.lookup,
                                      screen_name=screen_names_str)

        if response is None:
            break

        if type(response) is dict:  # Handle api quirk
            response = [response]
        for user_info in response:
            r.set(
                getRedisIdByScreenName(user_info['screen_name'], 'info.json'),
                json.dumps(user_info))
            r.set(getRedisIdByUserId(user_info['id'], 'info.json'),
                  json.dumps(user_info))
        info.extend(response)

    while len(user_ids) > 0:
        user_ids_str = ','.join([str(_id) for _id in user_ids[:100]])
        user_ids = user_ids[100:]

        response = makeTwitterRequest(t,
                                      t.users.lookup,
                                      user_id=user_ids_str)

        if response is None:
            break

        if type(response) is dict:  # Handle api quirk
            response = [response]
        for user_info in response:
            r.set(
                getRedisIdByScreenName(user_info['screen_name'], 'info.json'),
                json.dumps(user_info))
            r.set(getRedisIdByUserId(user_info['id'], 'info.json'),
                  json.dumps(user_info))
        info.extend(response)

    return info


# Convenience functions

def pp(_int):  # For nice number formatting
    locale.setlocale(locale.LC_ALL, '')
    return locale.format('%d', _int, True)


def getRedisIdByScreenName(screen_name, key_name):
    return 'screen_name$' + screen_name + '$' + key_name


def getRedisIdByUserId(user_id, key_name):
    return 'user_id$' + str(user_id) + '$' + key_name

# For calculating the max_id parameter from statuses, which is
# necessary in order to traverse a timeline in the v1.1 API.
# See https://dev.twitter.com/docs/working-with-timelines


def getNextQueryMaxIdParam(statuses):
    return min([status['id'] for status in statuses]) - 1

if __name__ == '__main__':  # For ad-hoc testing

    def makeTwitterRequest(t, twitterFunction, *args, **kwArgs):
        wait_period = 2
        while True:
            try:
                e = Exception()
                e.code = 401
                # e.code = 502
                # e.code = 503
                raise twitter.api.TwitterHTTPError(
                    e, "http://foo.com", "FOO", "BAR")
                return twitterFunction(*args, **kwArgs)
            except twitter.api.TwitterHTTPError, e:
                wait_period = handleTwitterHTTPError(e, t, wait_period)
                if wait_period is None:
                    return

    def _getRemainingHits(t):
        return 0

#   Comentado por javo: no deberia loguearse aca, porque necesita un id de usuario
#   t = login()
    makeTwitterRequest(t, t.friends.ids, screen_names=['SocialWebMining'])

# Agregado por Javo


def getUserTimeline(screen_name, t):
    import couchdb
    from couchdb.design import ViewDefinition
    from twitter__util import makeTwitterRequest
    from twitter__util import getNextQueryMaxIdParam


    TIMELINE_NAME = 'user' # XXX: IPython Notebook cannot prompt for input
    MAX_PAGES = 16 # XXX: IPython Notebook cannot prompt for input
    USER = screen_name # XXX: IPython Notebook cannot prompt for input

    KW = {  # For the Twitter API call
        'count': 200,
        'trim_user': 'true',
        'include_rts': 'false',  # No incluir retweets
        'since_id': 1
        }

    if TIMELINE_NAME == 'user':
        KW['screen_name'] = USER
    if TIMELINE_NAME == 'home' and MAX_PAGES > 4:
        MAX_PAGES = 4
    if TIMELINE_NAME == 'user' and MAX_PAGES > 16:
        MAX_PAGES = 16

    # Establish a connection to a CouchDB database
    server = couchdb.Server('http://localhost:5984')
    DB = 'tweets-%s-timeline' % (TIMELINE_NAME, )
    print DB
    if USER:
        DB = '%s-%s' % (DB, USER)

    print "Database: " + DB

    try:
        db = server.create(DB)
    except couchdb.http.PreconditionFailed, e:

        # Already exists, so append to it, keeping in mind that duplicates could occur

        db = server[DB]

        # Try to avoid appending duplicate data into the system by only retrieving tweets
        # newer than the ones already in the system. A trivial mapper/reducer combination
        # allows us to pull out the max tweet id which guards against duplicates for the
        # home and user timelines. This is best practice for the Twitter v1.1 API
        # See https://dev.twitter.com/docs/working-with-timelines

        def idMapper(doc):
            yield (None, doc['id'])

        def maxFindingReducer(keys, values, rereduce):
            return max(values)

        view = ViewDefinition('index', 'max_tweet_id', idMapper, maxFindingReducer,
                              language='python')
        view.sync(db)

        KW['since_id'] = int([_id for _id in db.view('index/max_tweet_id')][0].value)

    api_call = getattr(t.statuses, TIMELINE_NAME + '_timeline')
    tweets = makeTwitterRequest(t, api_call, **KW)
    db.update(tweets, all_or_nothing=True)

    page_num = 1
    while page_num < MAX_PAGES and len(tweets) > 0:

        # Necessary for traversing the timeline in Twitter's v1.1 API.
        # See https://dev.twitter.com/docs/working-with-timelines
        KW['max_id'] = getNextQueryMaxIdParam(tweets)

        api_call = getattr(t.statuses, TIMELINE_NAME + '_timeline')
        tweets = makeTwitterRequest(t, api_call, **KW)
        db.update(tweets, all_or_nothing=True)
        page_num += 1

    return "OK"

def getHomeTimeline(screen_name, t):
    import couchdb
    from couchdb.design import ViewDefinition
    from twitter__util import makeTwitterRequest
    from twitter__util import getNextQueryMaxIdParam


    TIMELINE_NAME = 'user' # XXX: IPython Notebook cannot prompt for input
    MAX_PAGES = 16 # XXX: IPython Notebook cannot prompt for input
    USER = screen_name # XXX: IPython Notebook cannot prompt for input
    EXCLUDE_OWN_TWEETS = True

    KW = {  # For the Twitter API call
        'count': 200,
        'include_rts': 'false',  # No incluir retweets
        'since_id': 1
        }

    if TIMELINE_NAME == 'user':
        KW['screen_name'] = USER
    if TIMELINE_NAME == 'home' and MAX_PAGES > 4:
        MAX_PAGES = 4
    if TIMELINE_NAME == 'user' and MAX_PAGES > 16:
        MAX_PAGES = 16

    # Establish a connection to a CouchDB database
    server = couchdb.Server('http://localhost:5984')
    DB = 'tweets-%s-timeline' % (TIMELINE_NAME, )
    print DB
    if USER:
        DB = '%s-%s' % (DB, USER)

    print "Database: " + DB

    try:
        db = server.create(DB)
    except couchdb.http.PreconditionFailed, e:

        # Already exists, so append to it, keeping in mind that duplicates could occur

        db = server[DB]

        # Try to avoid appending duplicate data into the system by only retrieving tweets
        # newer than the ones already in the system. A trivial mapper/reducer combination
        # allows us to pull out the max tweet id which guards against duplicates for the
        # home and user timelines. This is best practice for the Twitter v1.1 API
        # See https://dev.twitter.com/docs/working-with-timelines

        def idMapper(doc):
            yield (None, doc['id'])

        def maxFindingReducer(keys, values, rereduce):
            return max(values)

        view = ViewDefinition('index', 'max_tweet_id', idMapper, maxFindingReducer,
                              language='python')
        view.sync(db)

        KW['since_id'] = int([_id for _id in db.view('index/max_tweet_id')][0].value)

    api_call = getattr(t.statuses, TIMELINE_NAME + '_timeline')
    tweets = makeTwitterRequest(t, api_call, **KW)
    if EXCLUDE_OWN_TWEETS:
        tweetsFiltrados = [t for t in tweets if t['user']['screen_name'].lower() != screen_name.lower()]
    db.update(tweets, all_or_nothing=True)

    page_num = 1
    while page_num < MAX_PAGES and len(tweets) > 0:

        # Necessary for traversing the timeline in Twitter's v1.1 API.
        # See https://dev.twitter.com/docs/working-with-timelines
        KW['max_id'] = getNextQueryMaxIdParam(tweets)

        api_call = getattr(t.statuses, TIMELINE_NAME + '_timeline')
        tweets = makeTwitterRequest(t, api_call, **KW)
        db.update(tweets, all_or_nothing=True)
        page_num += 1

    return "OK"

def imprimirTweets(screen_name):
    import couchdb
    from couchdb.design import ViewDefinition

    DB = 'tweets-user-timeline-%s' % screen_name
    server = couchdb.Server('http://localhost:5984')
    db = server[DB]

    web.debug(DB);

    def traerTextos(doc):
        yield (None, doc['text'])

    view = ViewDefinition('index', 'traer_textos', traerTextos, language='python')
    view.sync(db)

    textos = [row.value for row in db.view('index/traer_textos')]


    return textos[0:20]



def analisisFrecuencia(screen_name):
    import couchdb
    from couchdb.design import ViewDefinition

    web.debug(screen_name)

    DB = 'tweets-user-timeline-%s' % screen_name
    server = couchdb.Server('http://localhost:5984')
    db = server[DB]
    FREQ_THRESHOLD = 3  # XXX: IPython Notebook cannot prompt for input



    # Map entities in tweets to the docs that they appear in
    def entityCountMapper(doc):
        if doc['entities']:
            if doc['entities'].get('user_mentions'):
                for user_mention in doc['entities']['user_mentions']:
                    yield ('@' + user_mention['screen_name'].lower(), [doc['_id'], doc['id']])
            if doc['entities'].get('hashtags'):
                for hashtag in doc['entities']['hashtags']:
                    yield ('#' + hashtag['text'], [doc['_id'], doc['id']])


    def summingReducer(keys, values, rereduce):
        if rereduce:
            return sum(values)
        else:
            return len(values)

    view = ViewDefinition('index', 'entity_count_by_doc', entityCountMapper,
                          reduce_fun=summingReducer, language='python')
    try:
        view.sync(db)
    except:
        logging.error('Fallo sincronizar la bd')
    # Print out a nicely formatted table. Sorting by value in the client is cheap and easy
    # if you're dealing with hundreds or low thousands of tweets


    entities_freqs = sorted([(row.key, row.value) for row in
                            db.view('index/entity_count_by_doc', group=True)],
                            key=lambda x: x[1], reverse=True)

    return entities_freqs


def procesarTweets(tweets):



    # Quita stopwords, hashtags, usuario y urls
    def quitarExcedente(tweet):
        lista = [palabra for palabra in tweet if palabra not in stopwords and
                                                         not re.match('^\#|@', palabra) and
                                                         not re.match('^http', palabra)
                                                     ]
        nuevaLista = []
        for w in lista:
            nuevaLista.append(re.sub('[.!,:;]', '', w))
        return nuevaLista

    import nltk
    import re
    from sets import Set

    stopwords = nltk.corpus.stopwords.words('english')+['-']

    respuesta = []

    for text in tweets:
        tweetLowercase = text.lower()
        listaPalabras = tweetLowercase.split()

        # Este metodo no se adapta bien a lenguaje poco formal
        #sentences = nltk.tokenize.sent_tokenize(textNuevo)
        #tokens = [nltk.tokenize.word_tokenize(s) for s in sentences]
#        arrayTextNuevo = []
#        for oracion in tokens:
#            arrayTextNuevo += oracion

        listaPalabras = quitarExcedente(listaPalabras)

        '''
        conjunto = Set()
        for w in listaPalabras:
            conjunto.add(re.sub('[.!,:;]', '', w))

        '''
        # Clasificamos las palabras en sustantivos, verbos, etc
        pos_tagged_tokens = [nltk.pos_tag(t) for t in [listaPalabras]][0]

        # Creamos un conjunto con clasifaiciones unicas
        conjuntoClasificacion = {}
        for (palabra, clasificacion) in pos_tagged_tokens:
            if clasificacion in conjuntoClasificacion:
                conjuntoClasificacion[clasificacion].add(palabra)
            else:
                conjuntoClasificacion[clasificacion] = set([palabra])

        #porter = nltk.PorterStemmer()

        #stemmed = [porter.stem(palabra) for palabra in listaPalabras]

        web.debug(conjuntoClasificacion)

        respuesta.append((text, conjuntoClasificacion))


    return respuesta
