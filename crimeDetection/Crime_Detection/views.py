from django.shortcuts import render
from django.contrib import auth
# Create your views here.
import pyrebase

import face_recognition
import cv2
from urllib.request import urlopen
import numpy as np
config={

    'apiKey': "AIzaSyDymA19Nq90InfXM9nuP8QRf4HYy1UWWI4",
    'authDomain': "crimedetectionproject.firebaseapp.com",
    'databaseURL': "https://crimedetectionproject.firebaseio.com",
    'projectId': "crimedetectionproject",
    'storageBucket': "crimedetectionproject.appspot.com",
    'messagingSenderId': "535048292753",
    'appId': "1:535048292753:web:aafdb608bbbc5de4ccf230",
    'measurementId': "G-WG2RF69NEN",
  }

firebase=pyrebase.initialize_app(config)
authe=firebase.auth()
database=firebase.database()
criminal_count=0
def index(request):
    return render(request,'index.html')

def signin(request):
    return render(request,'signin.html')

def signup(request):
    return render(request,'signup.html')

def postsignup(request):
    email=request.POST.get('email')
    name=request.POST.get('name')
    password=request.POST.get('password')
    user=authe.create_user_with_email_and_password(email,password)
    uid=user['localId']
    data={'name':name,'status':'0','deleted':'0'}
    database.child('Users').child(uid).child('data').set(data)
    return render(request,'signin.html')

def postsign(request):
    email=request.POST.get('email')
    password=request.POST.get('password')
    #try:
    user=authe.sign_in_with_email_and_password(email,password)
    session_id=user['idToken']
    request.session['uid']=str(session_id)
    #except:
    #    print('wrong credential')
    #    return render(request,'signin.html')
    return render(request,'postsign.html',{'email':email})
def signout(request):
    auth.logout(request)
    return render(request,'index.html')

def add_criminal(request):
    return render(request,'add_criminal.html')
def read_image(url):
    req=urlopen(url)
    arr=np.asarray(bytearray(req.read()),dtype=np.uint8)
    img=cv2.imdecode(arr,-1)
    img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    return img
def get_encodings(image):
    boxes=face_recognition.face_locations(image,model='cnn')
    encodings=face_recognition.face_encodings(image,boxes)
    return encodings
def post_add_criminal(request):
    name=request.POST.get('name')
    desc=request.POST.get('description')
    image_url=request.POST.get('url')
    print(image_url)
    ## to be continued by puneet
    img=read_image(image_url)
    enc=get_encodings(img)
    enc=enc[0]
    enc_str=', '
    enc=list(map(str,enc))
    enc_str=enc_str.join(enc)
    #criminal_count=criminal_count+1
    data={'id':'21','name':name,'description':desc,'status':'0','deleted':'0','image_url':image_url,'encoding':enc_str}
    database.child('Criminals').push(data)
    return render(request,'postsign.html')



def get_encoding_list():
    criminals=database.child('Criminals').get()
    a=criminals.val()
    print(a)
    k=[]
    encl=[]

    for key,value in a.items():
        k.append(key)
        encl.append(value['encoding'])
    #ans={'key':k,'enc':encl}
    ans=dict(zip(k,encl))
    return ans


def detect_face(request):
    return render(request,'detect_face.html')

def post_detect_face(request):
    url=request.POST.get('url')
    print('1')
    img=read_image(url)
    print('1')
    criminal_list=get_encoding_list()
    print('1')
    image_enc=get_encodings(img)
    print(len(image_enc))
    print('1')
    result_list=[]
    for encoding in image_enc:
        for criminal_key,criminal_encoding in criminal_list.items():
            criminal_encoding=criminal_encoding.split(', ')
            print('1')
            criminal_encoding=list(map(np.float64,criminal_encoding))
            print('2')
            result=face_recognition.compare_faces([criminal_encoding],encoding)
            if(result[0]==True):
                print('matched')
                result_list.append(criminal_key)
                break
    i=1
    print(result_list)
    names=[]
    desc=[]

    for items in result_list:
        criminal_face=database.child('Criminals').child(items).get()
        a=criminal_face.val()
        # for key,value in a.items():
        #     names.append(value['name'])
        #     encl.append(value['desc'])
        print(criminal_face.val())
    return render(request,'postsign.html')
