from headlines import Headlines
from synth import read_news

if __name__ == '__main__':
    read_news('What scoop would you like to hear today?')
    h = Headlines(method='TTS')
    news = h.news

    num_news = len(news)
    if num_news == 0:
        read_news("Sorry, no stories about " + h.topic + " . Pick another.")


    #read_news('give me the positive scoop on kittens from the new york post')
    read_news('Okay, I have {} {} stories about {}. How many would you like to hear?'.format(num_news, h.mood, h.topic))
    num_to_read = input("Input number of stories: ")
    print(news)
    count = 1
    for story in range(int(num_to_read)):
        read_news('story ' + str(count) + ': ' + news[story])
        count += 1

