# -*- coding: utf-8 -*-
import json
import os
import re
import urllib.request
import time

import multiprocessing as mp
from threading import Thread

from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template

app = Flask(__name__)

slack_token = "xoxb-505014660117-507419688659-B46gMt9uKkKlR9H0hMieu2fF"
slack_client_id = "505014660117.507354521492"
slack_client_secret = "7ac957152e9cb7d2baae311a198a2ecd"
slack_verification = "Ppvnfe3czvCunOV439uVLic1"
sc = SlackClient(slack_token)
tempStr = ""

# threading function
def processing_event(queue):
   while True:
       # 큐가 비어있지 않은 경우 로직 실행
       if not queue.empty():
           slack_event = queue.get()

           # Your Processing Code Block gose to here
           channel = slack_event["event"]["channel"]
           text = slack_event["event"]["text"]

           # 챗봇 크롤링 프로세스 로직 함수
           keywords = processing_function(text)

           # 아래에 슬랙 클라이언트 api를 호출하세요
           sc.api_call(
               "chat.postMessage",
               channel=channel,
               text=keywords
           )

           
# 크롤링 함수 구현하기
def processing_function(text):
   url = "https://docs.python.org/ko/3/library/functions.html"
   url_std = "https://docs.python.org/ko/3/library/stdtypes.html?highlight=strip#string-methods"
   url_lib = "https://docs.python.org/ko/3/library/"
   req = urllib.request.Request(url)
   req_std = urllib.request.Request(url_std)
   req_lib = urllib.request.Request(url_lib)
   temp = []
   tempStr3 = []

   sourcecode = urllib.request.urlopen(url).read()
   sourcecode_std = urllib.request.urlopen(url_std).read()
   sourcecode_lib = urllib.request.urlopen(url_lib).read()
   soup = BeautifulSoup(sourcecode, "html.parser")
   soup_std = BeautifulSoup(sourcecode_std, "html.parser")
   soup_lib = BeautifulSoup(sourcecode_lib, "html.parser")
    # stdtype페이지를 검색하기 위해서
    # soup 변수를 2개 선언하였음 (페이지가 다르기 떄문에)

   save = [] #function, class, method 중 하나의 계열에 해당하는 정보를 모아두는 곳
   save_lib = []
   save_more_info = []
   save_more_info_p = []
   keywords = [] # 실제 사용자가 검색한 정보를 저장하는 곳

   for funcList in soup.find_all("dl", class_="function"):
        save.append(funcList.get_text().strip())
   for classList in soup.find_all("dl", class_="class"):
        save.append(classList.get_text().strip())
   for methodList in soup_std.find_all("dl", class_="method"):
        save.append(methodList.get_text().strip())
   for libList in soup_lib.find_all("li", class_="toctree-l2"):
        save_lib.append(libList.get_text().strip())

   global tempStr # 결과를 저장할 임시 str변수
   text = str(text) # 사용자가 입력한 문자열을 str형으로 변환
   search = text[13:]
#    url_lib2 = "https://docs.python.org/ko/3/library/%s.html" %search
#    req_lib2 = urllib.request.Request(url_lib2)
#    sourcecode_lib2 = urllib.request.urlopen(url_lib2).read()
#    soup_lib2 = BeautifulSoup(sourcecode_lib2, "html.parser")
#    for libList2 in soup_lib2.find_all("ul", class_="simple"):
#        save_more_info.append(libList2.get_text().strip())
    # search는 사용자가 입력한 검색어
    # 유효한 문자를 걸러낸다.


   for j in range(len(save)) : 
      if save[j].startswith(search):
            # 내장함수의 이름 중 search와 일치하는지 검색
         tempStr = str(save[j])
         keywords.append(tempStr)
         break
      elif save[j].startswith("class %s" %search):
            # 클래스의 이름 중 search와 일치하는지 검색
         tempStr = str(save[j])
         keywords.append(tempStr)
         break
      elif save[j].startswith("str.%s" %search):
         # str 클래스의 메소드 중 search와 일치하는지 검색
         tempStr = str(save[j])
         keywords.append(tempStr)
         break
      elif save[j].startswith("bytes.%s" %search):
         # bytes 클래스의 메소드 중 search와 일치하는지 검색
         tempStr = str(save[j])
         keywords.append(tempStr)
         break
      else :
         tempStr = "%s는 내장함수 또는 메서드가 아닙니다." %search
   for k in range(len(save_lib)) :
      if save_lib[k].startswith(search):
         libList2 = ""
         # 내장함수의 이름 중 search와 일치하는지 검색
         url_lib2 = "https://docs.python.org/ko/3/library/%s.html" %search
         req_lib2 = urllib.request.Request(url_lib2)
         sourcecode_lib2 = urllib.request.urlopen(url_lib2).read()
         soup_lib2 = BeautifulSoup(sourcecode_lib2, "html.parser")
         for libList2 in soup_lib2.find_all("p"):#ul", class_="simple"):
            save_more_info_p.append(libList2.get_text().strip())
         for libList2 in soup_lib2.find_all("ul", class_="simple"):
            save_more_info.append(libList2.get_text().strip())
         for l in range(len(save_more_info_p)) : 
            if save_more_info_p[l].startswith(search) or save_more_info_p[l].startswith("This module") or save_more_info_p[l].startswith("이 모듈"):
               tempStr3.append(save_more_info_p[l])
               tempStr3.append("\n")
            else :
               pass     
         temp.append(save_lib[k])
         temp.append("\n")
         tempStr2 =  temp + tempStr3 + save_more_info
         break
      else :
         tempStr2 = "%s는 내장함수 또는 메서드가 아닙니다." %search
    #if libList2
    # 최종 결과물을 result에 저장
    # result에는 함수나 메소드 혹은 클래스의 설명이 들어있음

   #print(save_more_info_p)
   
   if tempStr == "%s는 내장함수 또는 메서드가 아닙니다." %search :
      result = tempStr2
   else :
      result = tempStr

    # 한글 지원을 위해 앞에 unicode u를 붙혀준다.
   print(search)
   return u"".join(result)

# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_event):
    print(slack_event["event"])

    if event_type == "app_mention":
        event_queue.put(slack_event)
#        channel = slack_event["event"]["channel"]
#        text = slack_event["event"]["text"]
#
#        keywords = _crawl_naver_keywords(text)
#        sc.api_call(
#            "chat.postMessage",
#            channel=channel,
#            text=keywords
#            
#        )

        return make_response("App mention message has been sent", 200,)

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})

@app.route("/listening", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data)

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                             "application/json"
                                                            })

    if slack_verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s" % (slack_event["token"])
        make_response(message, 403, {"X-Slack-No-Retry": 1})
    
    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return _event_handler(event_type, slack_event)

    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})

@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"

if __name__ == '__main__':
    event_queue = mp.Queue()

    p = Thread(target=processing_event, args=(event_queue,))
    p.start()
    print("subprocess started")

    app.run('127.0.0.1', port=8080)
    p.join()
