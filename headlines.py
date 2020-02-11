import requests
from bs4 import BeautifulSoup
from synth import *

class Headlines():

    def __init__(self, method):
        self.method = method
        self.mood, self.topic, self.paper = self.get_inputs()
        #self.mood, self.paper, self.topic = 'POSITIVE', 'BBC', 'puppy'
        self.paper_html = {
            'BBC': [{"itemprop": "headline"}, 'https://www.bbc.co.uk/search?q={}&filter=news&suggid='.format(self.topic)],
            'EXPRESS': [{"class": "post-title"},
                        'https://www.express.co.uk/search?s={}&order=relevant&section=77'.format(self.topic)],
            'CHICAGO': [{"class": "c-entry-box--compact__title"},
                        'https://chicago.suntimes.com/search?q={}'.format(self.topic)],
            'BOSTON': [{"class": "entry-title"},
                       'https://www.bostonherald.com/?s={}&post_type=&orderby=date&order=desc&sp%5Bf%5D=&sp%5Bt%5D='.format(
                           self.topic)],
            'NYPOST': [{"class": "entry-heading"}, 'https://nypost.com/search/{}/'.format(self.topic)]
        }
        self.url = self.paper_html[self.paper][1]
        self.response = requests.get(self.url).text
        self.news = self.get_headlines()


    def get_inputs(self):

        if self.method == 'ASR':

            #parse ASR input
            try:
                a = ASR()
                text_to_parse = a.text
                print('text to parse:', text_to_parse)
            except Exception as e:
                print(e)
                print("Sorry, I can't parse that. Have some happy news about puppies instead")
                # or raise exception and have below code in asr_demo
                read_news("Sorry, I can't parse that. Have some happy news about puppies instead")
                text_to_parse = "Give me the positive scoop on puppies from the BBC"
            text_to_parse = text_to_parse
            print('text to parse2:', text_to_parse)
            r = re.match(r'(Give me)( the )?(\w+)( scoop on )?(\w+)( from [t|T]he )?(\w+\s*\w*\s*\w*)+', str(text_to_parse))
            mood, topic, paper = r[3], r[5], r[7]

            print('Key words are: ', mood, topic, paper)
            return mood, topic, paper

        if self.method == 'TTS':
            print("Possible sentiments:"
                  "\n'good', 'great', 'happy', 'fabulous', 'excellent', 'positive'"
                  "\n'bad', 'terrible', 'awful', 'sad', 'ugly', 'negative'")
            mood = input("*** Enter a sentiment: ")
            list_pos = ['good', 'great', 'happy', 'fabulous', 'excellent', 'positive']
            list_neg = ['bad', 'terrible', 'awful', 'sad', 'ugly', 'negative']
            if mood in list_pos:
                mood = 'POSITIVE'
            elif mood in list_neg:
                mood = 'NEGATIVE'
            print("Possible newspapers:"
                  "\nBBC, NYPOST, BOSTON, CHICAGO, EXPRESS")
            paper = input("*** Enter a newspaper: ").upper()
            print("Pick any topic :) ")
            topic = input("*** Enter a topic: ").lower()
            return mood, topic, paper


    def get_headlines(self):
        # CONNECTS TO SENTIMENT ANALYSIS AND CREATES SOUP
        client = boto3.client('comprehend')
        soup = BeautifulSoup(self.response, 'lxml')
        headlines = soup.find_all(attrs=self.paper_html[self.paper][0])
        best = {}
        for headline in headlines:
            # CLEANS HEADLINES (words only, topic in headline)
            headline = re.sub(r'\n|\t', '', headline.text)
            if self.topic not in headline.lower():
                continue
            detection = client.detect_sentiment(Text=headline, LanguageCode='en')
            sentiment = detection['Sentiment']

            # IF SENTIMENT IS NEUTRAL BUT MOOD IS POS/NEG, SET TO POS/NEG BY SCORE

            if sentiment == 'NEUTRAL':
                if self.mood == 'POSITIVE' and detection['SentimentScore'][
                    'Positive'] > detection['SentimentScore']['Negative']:
                    sentiment = 'POSITIVE'
                if self.mood == 'NEGATIVE' and detection['SentimentScore'][
                    'Positive'] < detection['SentimentScore']['Negative']:
                    sentiment = 'NEGATIVE'
            if sentiment == self.mood:
                # CREATES DICT OF HEADLINE WITH SCORE
                sentiment = sentiment[0] + sentiment[1:len(sentiment)].lower()
                score = detection['SentimentScore'][sentiment]
                best[headline] = score
        # SORTS DICT AND CREATES LIST IN ORDER OF MOST POS OR MOST NEG
        best = {k: v for k, v in sorted(best.items(), key=lambda item: item[1], reverse=True)}
        sorted_news = list(best.keys())

        return sorted_news


