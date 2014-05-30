# -*- coding: cp1252 -*-
"""
Copyright [2014] [ASIER ARRANZ - asierarranz@gmail.com - www.asierarranz.com - @asierarranz]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import httplib2
import sys
import socket
import json
import datetime

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run

service=None
action=""
calid=""
eventId="fu672p4gue1q1lmf783l3q4ujg" #Pruebas - evento a borrar

client_id = "318681961923.apps.googleusercontent.com" # Sustituir por ID propios
client_secret = "I7qOFTrnsgt9c3rYO5fxYYIa" # Sustituir por ID propios (Ha sido modificado por seguridad)
scope = 'https://www.googleapis.com/auth/calendar'

flow = OAuth2WebServerFlow(client_id, client_secret, scope)


HOST = '192.168.100.50'   #Ip de escucha del servidor (dentro de su LAN)              
PORT = 7777              

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(1)


def jsonize(response):
    response=response.replace("u'","'")
    response=response.replace('"','^"')
    response=response.replace("'",'"')
    response=response.replace('^"',"'")
    response=response.replace("True",'"TRUE"')
    print str(response)
    return str(response)

    
def wait_cmd():
    print "Esperando comandos..."
    while 1:
        try:
            global action,service
            conn, addr = s.accept()
            request=""
            print "b"
            print 'Conexion: ', addr
            while 1:
                data = conn.recv(1024)
                if not data: break
                print "----------------------"
                print "He recibido la cadena: "
                print data
                print "----------------------"
                try:
                    request=process_action(data)
                    print "1"
                    print request
                except Exception as e:
                    print str(e)
                    conn.sendall(str(e)+"\r\n")
                    conn.close()
                    break
                print "2"
                print request
                conn.sendall(request+"\r\n")
                conn.close()
                print ""
                print "-----===== JSON ENVIADO =====-----"
                print request
                print "-----===== JSON ENVIADO =====-----"
                print ""
                f = open('json_enviado.txt', 'w')
                f.write(request)
                f.close()
                
        except Exception as e:  
            pass
        

def log(logdata):
    now=datetime.datetime.now()
    f = open('log'+str(now.year)+str(now.month)+str(now.day)+'.txt', 'a')
    f.write(str(now.hour)+":"+str(now.minute)+":"+str(now.second)+"|   "+logdata+"\r\n")
    f.close()
    

def insertCal(data):
    
    print "Insert"
    eventdict=json.loads(data)
    log("Insert " + eventdict["CalendarId"])
    response=service.events().insert(calendarId=eventdict["CalendarId"], body=eventdict["Items"]).execute()
    jsonized=jsonize(str(response))
    return jsonized

def deleteCal(data):
    print "Delete"
    eventdict=json.loads(data)
    log("Delete " + eventdict["CalendarId"])
    response=service.events().delete(calendarId=eventdict["CalendarId"],eventId=eventdict["EventId"]).execute()
    jsonized=jsonize(str(response))
    return jsonized

def listCal(data):
    print "list"
    eventdict=json.loads(data)
    log("List " + eventdict["CalendarId"])
    request=service.events().list(calendarId=eventdict["CalendarId"])
    while request != None:
                  response = request.execute()
                  request = service.events().list_next(request, response)
                  jsonized=jsonize(str(response))
                  jsonized=str(jsonized)
    return jsonized

def process_action(data):
  global sevice,action,calid
  recibido=json.loads(data)
  comando=recibido["Command"]
  service_action=None 
  if "insert" in comando:
      service_action=insertCal(data)
  if "delete" in comando:
      service_action=deleteCal(data)
  if "list" in comando:
      service_action=listCal(data)
  print "devolviendo ",
  print service_action
  return service_action


def main():
  global service
  storage = Storage('credentials.dat')
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run(flow, storage)

  http = httplib2.Http()
  http = credentials.authorize(http)

  service = build('calendar', 'v3', http=http)

  try:
    wait_cmd()


  except AccessTokenRefreshError:
    print ('Error de auth.')

if __name__ == '__main__':
  main()
