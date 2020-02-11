from headlines import Headlines
from synth import read_news

if __name__ == '__main__':

    h = Headlines(method='ASR')
    news = h.news

    num_news = len(news)
    read_news('Okay, I have {} {} stories about {}. How many would you like to hear?'.format(num_news, h.mood, h.topic))
    num_to_read = input("Input number of stories: ")
    print(news)

    # read out stories
    count = 1
    for story in range(int(num_to_read)):
        read_news('story ' + str(count) + ': ' + news[story])
        count += 1
