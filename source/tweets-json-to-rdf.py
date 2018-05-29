"""Convert Tweets from Twitter API json format into RDF using SIOC Ontology
 The output is in Turtle format ready to be imported in any graph database
"""

__author__ = "Abdurrahman Ghanem"


import rdflib as rdf
from rdflib.namespace import FOAF, DC, RDF, XSD
import json
import os
import sys
from datetime import datetime


SIOC = rdf.Namespace('http://rdfs.org/sioc/ns#')
SIOC_TYPES = rdf.Namespace('http://rdfs.org/sioc/types#')
SIOC_QUOTES = rdf.Namespace('http://rdfs.org/sioc/quotes#')
GN = rdf.Namespace('http://www.geonames.org/ontology#')
DCTERMS = rdf.Namespace('http://purl.org/dc/terms/')
SEAS = rdf.Namespace('https://w3id.org/seas/')
PROV = rdf.Namespace('http://www.w3.org/ns/prov#')
STO = rdf.Namespace('https://w3id.org/i40/sto#')
TWITTER = rdf.Namespace('http://twitter.com/')
IOL = rdf.Namespace('http://www.ontologydesignpatterns.org/ont/dul/IOLite.owl#')
D2RQ = rdf.Namespace('http://www.wiwiss.fu-berlin.de/suhl/bizer/D2RQ/0.1#')


class twitter_json_to_rdf(object):
    """
    converting twitter API's json into rdf following SIOC RDFS
    """
    def __init__(self,filename, write_to):
        try:
            self.tweets_file = open(filename, "r")
            if write_to is not None:
                self.export_file = write_to
            else:
                self.export_file = os.path.splitext(filename)[0] + ".ttl"
            self.graph = rdf.Graph()
        except IOError as e:
            print("error opening file" + str(e))

    def process_tweets(self):
        if self.tweets_file is not None:
            for line in self.tweets_file:
                tweet = json.loads(line)
                self.convert_tweet(tweet)

    def convert_tweet(self, tweet_dict):
        self.extract_twitter(tweet_dict)

        tweet_uri = self.get_tweet_uri(tweet_dict=tweet_dict)
        tweet_id = self.read_key_from_dict(tweet_dict, "id")
        text = self.retrieve_original_text(self.read_key_from_dict(tweet_dict, "text") or self.read_key_from_dict(tweet_dict, "full_text"))
        creator = self.get_twitter_uri(self.read_key_from_dict(tweet_dict, "user"))
        urls = [url["expanded_url"] for url in self.read_key_from_dict(self.read_key_from_dict(tweet_dict, "entities"), "urls", is_sequence=True)]
        lang = self.read_key_from_dict(tweet_dict, "lang")
        location = self.get_location(tweet_dict)
        device = self.get_device(self.read_key_from_dict(tweet_dict, "source"))
        hashtags = [self.retrieve_original_text(ht["text"]) for ht in self.read_key_from_dict(self.read_key_from_dict(tweet_dict, "entities"), "hashtags", is_sequence=True)]
        mentions = [self.get_twitter_uri(mn) for mn in self.read_key_from_dict(self.read_key_from_dict(tweet_dict, "entities"), "user_mentions", is_sequence=True)]
        medias = [self.get_media_info(m) for m in self.read_key_from_dict(self.read_key_from_dict(tweet_dict, "extended_entities"), "media", is_sequence=True)]

        reply_params = self.is_reply_tweet(tweet_dict)
        if reply_params is not None:
            reply_to_tweet = self.get_tweet_uri(status_id=reply_params[0], screen_name=reply_params[1])
            self.add_triple_to_graph(tweet_uri, SIOC.reply_of, reply_to_tweet)

        quote_params = self.is_quote_tweet(tweet_dict)
        if quote_params is not None:
            quote_tweet = self.get_tweet_uri(screen_name=quote_params[0], status_id=quote_params[1])
            self.convert_tweet(self.read_key_from_dict(tweet_dict, "quoted_status"))
            self.add_triple_to_graph(tweet_uri, PROV.wasQuotedFrom, quote_tweet)

        retweet_params = self.is_retweet(tweet_dict)
        if retweet_params is not None:
            retweet_tweet = self.get_tweet_uri(screen_name=retweet_params[0], status_id=retweet_params[1])
            self.convert_tweet(self.read_key_from_dict(tweet_dict, "retweeted_status"))
            self.add_triple_to_graph(tweet_uri, DCTERMS.references, retweet_tweet)

        created_at = self.read_key_from_dict(tweet_dict, "created_at")
        cdate = self.create_datetime(created_at)

        self.add_triple_to_graph(tweet_uri, SIOC.type, SIOC.microblogPost)
        self.add_literal_to_subject(tweet_uri, SIOC.id, tweet_id)
        self.add_literal_to_subject(tweet_uri, SIOC.content, text, lang=lang)
        self.add_literal_to_subject(tweet_uri, SIOC.has_creator, creator)
        self.add_triple_to_graph(creator, SIOC.creator_of, tweet_uri)
        self.add_literals_to_subject(tweet_uri, STO.hasTag, hashtags)
        self.add_triples_to_graph(tweet_uri, SIOC.mentions, mentions)
        self.add_literals_to_subject(tweet_uri, SIOC.links_to, urls)
        # for hashtag in hashtags:
        #     self.add_literal_to_subject(tweet_uri, STO.hasTag, hashtag)
        # for mention in mentions:
        #     self.add_triple_to_graph(tweet_uri, SIOC.mentions, mention)
        # for url in urls:
        #     self.add_literal_to_subject(tweet_uri, SIOC.links_to, url)
        for uri, id, url, type in medias:
            self.add_triple_to_graph(uri, RDF.type, IOL.MultimediaObject)
            self.add_literal_to_subject(uri, SIOC.id, id)
            self.add_literal_to_subject(uri, SIOC.link, url)
            self.add_literal_to_subject(uri, D2RQ.mediaType, type)
        self.add_literal_to_subject(tweet_uri, DCTERMS.language, lang)
        self.add_literal_to_subject(tweet_uri, GN.locatedIn, location)
        self.add_literal_to_subject(tweet_uri, SEAS.device, device)
        self.add_literal_to_subject(tweet_uri, DCTERMS.created, self.get_rdf_datetime(cdate), datatype=XSD.datetime)

    def extract_twitter(self, tweet):
        user_dict = self.read_key_from_dict(tweet, "user")

        if user_dict is not None:
            screen_name = self.read_key_from_dict(user_dict, "screen_name")
            user_id = self.read_key_from_dict(user_dict, "id")
            name = self.retrieve_original_text(self.read_key_from_dict(user_dict, "name"))
            url = "http://twitter.com/" + screen_name + "/"
            profile_img = self.read_key_from_dict(user_dict, "profile_image_url")
            verified = self.read_key_from_dict(user_dict, "verified")
            description = self.retrieve_original_text(self.read_key_from_dict(user_dict, "description"))
            location = self.read_key_from_dict(user_dict, "location")
            main_lang = self.read_key_from_dict(user_dict, "lang")
            created_at = self.read_key_from_dict(user_dict, "created_at")
            cdate = self.create_datetime(created_at)

            if screen_name is not None:
                user = self.get_twitter_uri(user_dict)
                self.add_triple_to_graph(user, RDF.type, SIOC_TYPES.UserAccount)
                self.add_literal_to_subject(user, SIOC.name, screen_name)

                self.add_literal_to_subject(user, SIOC.id, user_id)
                self.add_literal_to_subject(user, FOAF.name, name)
                self.add_literal_to_subject(user, SIOC.link, url)
                self.add_literal_to_subject(user, SIOC.avatar, profile_img)
                self.add_literal_to_subject(user, SIOC.description, description)
                self.add_literal_to_subject(user, GN.locatedIn, location)
                self.add_literal_to_subject(user, DCTERMS.language, main_lang)
                self.add_literal_to_subject(user, DCTERMS.created, self.get_rdf_datetime(cdate), datatype=XSD.datetime)

                ver_val = "verified" if verified else "not verified"
                self.add_literal_to_subject(user, SIOC.has_group, ver_val)

    def export_rdf(self, format="turtle"):
        if self.export_file is not None:
            try:
                self.graph.serialize(destination=self.export_file, format=format)
            except IOError as e:
                print("error writing to file" + str(e))

    def add_triple_to_graph(self, subj, pred, obj):
        if all(v is not None for v in [subj, pred, obj]):
            self.graph.set((subj, pred, obj))

    def add_triples_to_graph(self, subj, pred, objs):
        if all(v is not None for v in [subj, pred, objs]) and hasattr(objs, "__len__"):
            for obj in objs:
                self.graph.set((subj, pred, obj))

    def add_literal_to_subject(self, subj, pred, value, lang=None, datatype=None):
        if value is not None:
            if not isinstance(value, str) or len(value) > 0:
                if datatype is not None:
                    literal = rdf.Literal(value, datatype=datatype)
                elif lang is not None:
                    literal = rdf.Literal(value, lang=lang)
                else:
                    literal = rdf.Literal(value)
                self.add_triple_to_graph(subj, pred, literal)

    def add_literals_to_subject(self, subj, pred, values, lang=None):
        if values is not None and hasattr(values, "__len__"):
            for value in values:
                self.add_literal_to_subject(subj, pred, value, lang=lang)

    def get_twitter_uri(self, user_dict):
        if "screen_name" in user_dict:
            return rdf.URIRef("http://twitter.com/" + user_dict["screen_name"] + "/")

    def get_tweet_uri(self, tweet_dict=None, screen_name=None, status_id=None):
        if tweet_dict is not None and "user" in tweet_dict and "screen_name" in tweet_dict["user"]:
            return rdf.URIRef("http://twitter.com/" + tweet_dict["user"]["screen_name"] + "/status/" + tweet_dict["id_str"] + "/")
        elif screen_name is not None and status_id is not None:
            return rdf.URIRef("http://twitter.com/" + screen_name + "/status/" + str(status_id) + "/")

    def retrieve_original_text(self, text):
        return text.encode('utf-16').decode('utf-16')

    def get_location(self, tweet_dict):
        if "place" in tweet_dict and tweet_dict["place"] is not None:
            return tweet_dict["place"]["name"] + ", " + tweet_dict["place"]["country_code"]

    def get_device(self, device_str):
        if "Android" in device_str:
            return "Android"
        elif "iPhone" in device_str:
            return "iPhone"
        elif "Twitter Web Client" in device_str:
            return "Web"

    def get_media_info(self, media_dict):
        if all(v in media_dict and len(media_dict[v]) > 0 for v in ["id_str", "type", "url"]):
            return rdf.URIRef(media_dict["expanded_url"]), media_dict["id"], media_dict["url"], media_dict["type"]

    def is_reply_tweet(self, tweet_dict):
        if "in_reply_to_status_id" in tweet_dict:
            return tweet_dict["in_reply_to_status_id"], tweet_dict["in_reply_to_screen_name"]

    def is_quote_tweet(self, tweet_dict):
        if "quoted_status" in tweet_dict:
            return tweet_dict["quoted_status"]["user"]["screen_name"], tweet_dict["quoted_status"]["id"]

    def is_retweet(self, tweet_dict):
        if "retweeted_status" in tweet_dict:
            return tweet_dict["retweeted_status"]["user"]["screen_name"], tweet_dict["retweeted_status"]["id"]

    def read_key_from_dict(self, dict, key, is_sequence=False):
        if dict is not None and key in dict:
            return dict[key]
        if is_sequence:
            return []

    def create_datetime(self, dtstring):
        if dtstring is not None:
            return datetime.strptime(dtstring, '%a %b %d %H:%M:%S %z %Y')

    def get_rdf_datetime(self, dt):
        if dt is not None:
            return dt.strftime('%Y-%m-%dT%H:%M:%S')

    def __del__(self):
        if self.tweets_file is not None:
            self.tweets_file.close()


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        file_name = sys.argv[1]
        export_file = sys.argv[2] if len(sys.argv) == 3 else None
        graph_builder = twitter_json_to_rdf(file_name, export_file)
        graph_builder.process_tweets()
        graph_builder.export_rdf()
    else:
        print("insufficient parameters")

