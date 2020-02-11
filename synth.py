from __future__ import print_function

# #from audio import *
# from play import *
# from pydub import AudioSegment
# from pydub.playback import play
# from playsound import playsound
import os
import time
import boto3
import urllib
import json
import random
import re

def read_news(news):
    #mood, topic, paper = h.mood, h.topic, h.paper
    polly_client = boto3.Session(
        aws_access_key_id='AKIA2BTSLOSNK3YOR2XO',
        aws_secret_access_key='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',
        region_name='eu-west-1').client('polly')
    print("New story being spoken: ", news)
    response = polly_client.synthesize_speech(VoiceId='Kendra',
                                              Engine='neural',
                                              OutputFormat='mp3',
                                              Text=news,)

### MAKE VARIABLES FOR FILE NAME AND ALSO NORMALISE SPELLINGS FOR PAPERS
    #mp3_name = mood+'_'+paper+'_'+topic+'.mp3'
    mp3_name = 'filex.mp3'

    print('File name: ', mp3_name)
    file = open(mp3_name, 'wb')
    file.write(response['AudioStream'].read())
    os.system("mpg123 " + mp3_name)
    file.close()


sel_dict = {'1':['Give me the positive scoop about rhinos from the BBC', 'pos_bbc_rhinos.mp3'],
            '2':['Give me the positive scoop about kittens from the NYPOST', 'pos_nypost_kitten.mp3'],
            '3':['Give me the negative news about wuhan from the EXPRESS', 'neg_exp_wuhan.mp3']}


class ASR():
    def __init__(self):
        self.tmp, self.asr_rec_file, self.sentence = self.get_args()
        self.text = self.asr()

    def get_args(self):
        read_news('What scoop would you like to hear today?')

        print('Your options with ASR are currently limited due to AWS offline system:')
        print('1 Give me the positive scoop about rhinos from the BBC,'
              '\n2 Give me the positive scoop about kittens from the NYPOST,'
              '\n3 Give me the negative news about wuhan from the EXPRESS')
        choice = input('Please select option 1, 2, or 3 above')
        try:
            filename = sel_dict[choice][1]
            sentence = sel_dict[choice][0]
        except:
            choice = input('Try again. Please select option 1, 2, or 3 above')
            filename = sel_dict[choice][1]
            sentence = sel_dict[choice][0]

        count = random.random()
        tmp_name = 'test' + str(count)
        count += 1
        return tmp_name, filename, sentence

    def asr(self):
        print('Starting ASR...')
        transcribe = boto3.client('transcribe')
        job_name = self.tmp
        '''online, asr_rec_file would be created live. The way it is, we create it artificially and in a rather circular way,
        create it by passing a pre-synthesised sentences into the transcriber, then parse the transcription to identify
        key words incl. mood, topic, and paper. These then get plugged into Headlines() to have their sentiment recognised,
        then appropriate headlines get passed to the synthesiser to be said out loud'''
        job_uri = "s3://headlines-asr/" + self.asr_rec_file
        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': job_uri},
            MediaFormat='mp3',
            LanguageCode='en-IE'
        )
        while True:
            status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
            if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
                break
            print("Not ready yet... (but I'll probably get there... ?)")
            time.sleep(10)

        if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
            response = urllib.request.urlopen(status['TranscriptionJob']['Transcript']['TranscriptFileUri'])
            data = json.loads(response.read())
            text = data['results']['transcripts'][0]['transcript']
            print('Transcription recognised: ', text)
            text = re.sub(r'(New York Post)', 'NYPOST', text)
            return str(text)
