# -*- coding: utf-8 -*-

import twitter

def login(usuario_id):

    # Go to http://twitter.com/apps/new to create an app and get these items
    # See also http://dev.twitter.com/pages/oauth_single_token

    CONSUMER_KEY = 'oyEys6d4bYh3VVMHE8cvAw'
    CONSUMER_SECRET = 'wqHM5ZuDOQwRmD1VzBjLxHH6pKu9FAfo1gPp7nUSKc4'

    import couchdb
    server = couchdb.Server('http://localhost:5984')
    db = server['usuarios']
    usuario = db.get(usuario_id)
    
    oauth_token = usuario['oauth_token']
    oauth_token_secret = usuario['oauth_token_secret']
         
    return twitter.Twitter(domain='api.twitter.com', api_version='1.1',
                        auth=twitter.oauth.OAuth(oauth_token, oauth_token_secret,
                        CONSUMER_KEY, CONSUMER_SECRET))

if __name__ == '__main__':
    login()
