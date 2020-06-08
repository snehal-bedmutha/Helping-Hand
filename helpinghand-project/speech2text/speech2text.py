import speech_recognition as sr

import os

from pydub import AudioSegment
from pydub.silence import split_on_silence

from youtube_transcript_api import YouTubeTranscriptApi


def transcription(name, url):
    # video_id_list ={"knitting":'PLYfCBK8IplO6v0QjCj-TSrFUXnRV0WxfE'}
    # for id,value in video_id_list.items():
    video_id = url.split("=")[1]
    print(video_id)
    dict =YouTubeTranscriptApi.get_transcript(video_id)
    file = open(r"transcript_"+name+".txt", "a+")

    for i in dict:
        file.write(i["text"])
    file.close()

