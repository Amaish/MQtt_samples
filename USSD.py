import os
from flask import Flask
from flask import request
from flask import make_response
import time
import paho.mqtt.client as paho
import random
from AfricasTalkingGateway import AfricasTalkingGateway, AfricasTalkingGatewayException

broker="sungura1-angani-ke-host.africastalking.com"
port = 10883                         #Broker port
user = "amaina"                    #Connection username
password = "TamaRind"            #Connection password
client= paho.Client("Anthony-001") #create client object client1.on_publish = on_publish #assign function to callback client1.connect(broker,port) #establish connection client1.publish("house/bulb1","on")
client.username_pw_set(user, password=password)    #set username and password
print("connecting to broker ",broker)
client.connect(broker, port)#connect
client.loop_start() #start loop to process received messages

def send_sms(message, readings):# the send message function sends text to user
    username = "sandbox"
    apikey   = "f718b2abdabd86b7c0d2fea67b8a8e8ac459bdde82db1522858f70272a6b9a00"
    to = request.values.get("phoneNumber", None)
    message = message + str(readings)
    from_ = "KPLC"
    gateway = AfricasTalkingGateway(username, apikey)
    try:
       
        results = gateway.sendMessage(to, message, from_)
        
        for recipient in results:
            # status is either "Success" or "error message"
            print 'number=%s;status=%s;messageId=%s;cost=%s' % (recipient['number'],
                                                                recipient['status'],
                                                                recipient['messageId'],
                                                                recipient['cost'])
    except AfricasTalkingGatewayException, e:
        print 'Encountered an error while sending: %s' % str(e)

app = Flask(__name__)



@app.route('/api/ussd/callback', methods=['POST', 'GET'])
def ussd_callback():
    session_id      = request.values.get("sessionId", None)
    serviceCode     = request.values.get("serviceCode", None)
    phoneNumber     = request.values.get("phoneNumber", None)
    text            = request.values.get("text", None)

    texttoarray     = text.split('*')
    userResponse    = texttoarray[-1]
    
    #serve menus based on text
    if text == "":
        menu_text = "CON Welcome to KPLC prepaid, please choose an option:\n"
        menu_text += "1. Check my Account information\n"
        menu_text += "2. Top-Up my balance\n"
      
    elif text =="1":
        menu_text = "CON Choose the account information that you want to view \n"
        menu_text += "1. My Token balance\n"
        menu_text += "2. My Account number \n"

    elif text =="2":
        menu_text = "CON Please enter the amount"
            
    elif text =="1*1":
        token = random.randrange(16,38)
        menu_text = "END Your Token balance is: "+ str(token)
        client.publish("amaina/token",token)
        send_sms("Your remaining tokens are: ", token)
        time.sleep(2)
        
    elif text =="1*2":
        menu_text = "END Your account number is ACOO10SWO2101."
    
    elif text =="2*"+userResponse:
        client.publish("amaina/amount",userResponse)
        client.subscribe("amaina/amount")
        send_sms("Thank you the amount paid in is: ", userResponse)
        time.sleep(2)
        menu_text = "END Thank-you"
    
    resp = make_response(menu_text, 200)
    resp.headers['Content-Type'] = "text/plain"
    return resp


if __name__ == "__main__":
        app.run()

