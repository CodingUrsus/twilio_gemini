## receiving general messages
import os
import requests
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from pickle import TRUE
import PIL.Image
import google.generativeai as genai

# need account SID and auth token to interface with twilio
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


app = Flask(__name__)

image_storage_directory = os.getenv("IMAGE_STORAGE_LOCATION")

# the function below takes the directory location of the image, and the text body from the text to more effectively
# prompt gemini-pro when formulating a response
def gemini_genie(full_image_name, text_body):
    # need api key to interact with gemini pro api
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    if full_image_name:
        try:
            img = PIL.Image.open(full_image_name)
            vision_model = genai.GenerativeModel('gemini-pro-vision')
            # uses the image and text from the text message to generate content response
            response = vision_model.generate_content([str(text_body), img], stream=True)
            response.resolve()
            return response.text
        except FileNotFoundError:
            print("Image file not found:", full_image_name)
            return "Image not found."
    else:
        # this basically uses the non-vision model for text only requests, then returns the response
        text_answer_model = genai.GenerativeModel('gemini-pro')
        response = text_answer_model.generate_content(str(text_body), stream=True)
        response.resolve()
        return(response.text)

@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    # formulate response below
    resp = MessagingResponse()
    body_text = request.values['Body']
    if request.values['NumMedia'] != '0':
        # need a unique file name so this uses the message SID
        filename = request.values['MessageSid']  + '.jpg'
        with open('{}/{}'.format(image_storage_directory, filename), 'wb') as imagef:
           image_url = request.values['MediaUrl0']
           response = requests.request('GET', image_url, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN))
           imagef.write(response.content)
           print("Image saved to: " + str(image_storage_directory + "/" + filename)) # provide heads up on image save

        text_answer = gemini_genie(str(image_storage_directory + "/" + filename), body_text)

        resp.message(str(text_answer))
    else:
        text_answer = gemini_genie(full_image_name=0, text_body = str(body_text))
        resp.message(str(text_answer))

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)