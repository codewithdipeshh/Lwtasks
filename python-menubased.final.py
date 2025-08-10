import streamlit as st
import pandas as pd
from datetime import date
import time
import os
import requests
import random

# --- Import necessary libraries for each app ---
# It's good practice to handle potential import errors
try:
    import pywhatkit
    import pyautogui
    from twilio.rest import Client
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders
    from instagrapi import Client as InstaClient
    from openai import OpenAI
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from PIL import Image
except ImportError as e:
    st.error(f"A library is not installed. Please run 'pip install ...' for the missing library. Error: {e}")
    st.stop()



# --- 1. WHATSAPP SENDER APP ---

def app_whatsapp_sender():
    st.title("WhatsApp Instant Auto-Sender")
    st.markdown("Send instant WhatsApp messages with auto-send.")
    st.warning("This tool will take control of your mouse and keyboard to automate sending.")

    with st.form("whatsapp_form"):
        phone_number = st.text_input("Recipient's Phone Number", placeholder="Start with country code, e.g., +91")
        message = st.text_area("Message to Send")
        submitted = st.form_submit_button("Send Instantly")

        if submitted:
            if not phone_number or not message:
                st.warning("Please provide both a phone number and a message.")
            else:
                try:
                    with st.spinner("Opening WhatsApp Web and sending message... Please wait."):
                        # pywhatkit opens WhatsApp Web
                        pywhatkit.sendwhatmsg_instantly(phone_number, message, wait_time=15, tab_close=True)
                        # Give time for the message to be typed
                        time.sleep(12) 
                        # Use pyautogui to press Enter
                        pyautogui.press("enter")
                    st.success("Message sent successfully!")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
                    st.info("Common issues: Is WhatsApp Web linked? Is the phone number correct?")


# --- 2. TWILIO CALL APP ---

def app_twilio_call():
    st.title("Make a Phone Call with Twilio")
    st.markdown("Initiate a phone call that speaks a message to the recipient.")
    
    st.subheader("Twilio Credentials")
    st.info("Enter your Twilio credentials below. You can find these on your Twilio dashboard.")
    account_sid = st.text_input("Twilio Account SID", type="password")
    auth_token = st.text_input("Twilio Auth Token", type="password")
    twilio_number = st.text_input("Your Twilio Phone Number", placeholder="e.g., +1234567890")

    st.markdown("---")

    with st.form("call_form"):
        to_number = st.text_input("Recipient's Phone Number", placeholder="e.g., +919876543210")
        speak_text = st.text_area("What should the call say?")
        submitted = st.form_submit_button("Make Call")

        if submitted:
            if not all([account_sid, auth_token, twilio_number, to_number, speak_text]):
                st.warning("Please fill in all fields.")
            else:
                try:
                    with st.spinner("Initiating call..."):
                        client = Client(account_sid, auth_token)
                        twiml_message = f"<Response><Say>{speak_text}</Say></Response>"
                        call = client.calls.create(
                            twiml=twiml_message,
                            to=to_number,
                            from_=twilio_number
                        )
                    st.success(f"Call initiated successfully!")
                except Exception as e:
                    st.error(f"Error making call: {e}")


# --- 3. GMAIL SENDER APP ---

def app_gmail_sender():
    st.title("Send Email via Gmail")
    st.markdown("Send an email, with an optional attachment, using your Gmail account.")

    st.subheader("Gmail Credentials")
    st.info("You must use a Google 'App Password' for this to work, not your regular password.")
    sender_email = st.text_input("Your Gmail Address", placeholder="your.email@gmail.com")
    app_password = st.text_input("Your Gmail App Password", type="password")
    
    st.markdown("---")

    with st.form("email_form"):
        receiver_email = st.text_input("Receiver Email", placeholder="recipient@example.com")
        subject = st.text_input("Subject")
        message = st.text_area("Message Body")
        uploaded_file = st.file_uploader("📎 Attach a file (optional)")
        submitted = st.form_submit_button("Send Email")

        if submitted:
            if not all([sender_email, app_password, receiver_email, subject, message]):
                st.warning("Please fill in all required fields.")
            else:
                try:
                    with st.spinner("Building and sending email..."):
                        # Build email
                        msg = MIMEMultipart()
                        msg["From"] = sender_email
                        msg["To"] = receiver_email
                        msg["Subject"] = subject
                        msg.attach(MIMEText(message, "plain"))

                        # Attach file if it exists
                        if uploaded_file is not None:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(uploaded_file.read())
                            encoders.encode_base64(part)
                            part.add_header("Content-Disposition", f"attachment; filename={uploaded_file.name}")
                            msg.attach(part)
                        
                        # Send email
                        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                            server.login(sender_email, app_password)
                            server.send_message(msg)
                    st.success("Email sent successfully!")
                except Exception as e:
                    st.error(f"Failed to send email: {e}")


# --- 4. INSTAGRAM POSTER APP ---

def app_instagram_poster():
    st.title("Instagram Photo Uploader")
    st.markdown("Post a photo with a caption directly to your Instagram account.")

    st.subheader("Instagram Login")
    username = st.text_input("Instagram Username")
    password = st.text_input("Instagram Password", type="password")
    
    st.markdown("---")

    with st.form("insta_form"):
        uploaded_file = st.file_uploader("Upload an image (JPG only)", type=["jpg", "jpeg"])
        caption = st.text_area("Write a caption")
        submitted = st.form_submit_button("Post to Instagram")

        if submitted:
            if not all([username, password, uploaded_file]):
                st.warning("Please provide your login details and upload a photo.")
            else:
                temp_file_path = "temp_image.jpg"
                try:
                    with st.spinner("Logging in and posting to Instagram..."):
                        # Save the uploaded file temporarily
                        with open(temp_file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        # Login and upload
                        cl = InstaClient()
                        cl.login(username, password)
                        cl.photo_upload(temp_file_path, caption)
                    st.success("Successfully posted to Instagram!")
                except Exception as e:
                    st.error(f"Failed to post: {e}")
                finally:
                    # Clean up by removing the temporary file
                    if os.path.exists(temp_file_path):
                        os.remove(temp_file_path)


# --- 5. TWILIO SMS APP ---

def app_twilio_sms():
    st.title("SMS Sender with Twilio")
    st.markdown("Send a simple text message (SMS) to any phone number.")

    st.subheader("Twilio Credentials")
    st.info("Enter your Twilio credentials below. These can be the same as the Call app.")
    account_sid = st.text_input("Twilio Account SID", type="password")
    auth_token = st.text_input("Twilio Auth Token", type="password")
    twilio_number = st.text_input("Your Twilio Phone Number", placeholder="e.g., +1234567890")

    st.markdown("---")

    with st.form("sms_form"):
        to_number = st.text_input("Recipient's Phone Number", placeholder="e.g., +919876543210")
        message_body = st.text_area("Enter your message")
        submitted = st.form_submit_button("Send SMS")
        
        if submitted:
            if not all([account_sid, auth_token, twilio_number, to_number, message_body]):
                st.warning("Please fill in all fields.")
            else:
                try:
                    with st.spinner("Sending SMS..."):
                        client = Client(account_sid, auth_token)
                        message = client.messages.create(
                            body=message_body,
                            from_=twilio_number,
                            to=to_number
                        )
                    st.success(f"Message sent!:")
                except Exception as e:
                    st.error(f"Error sending SMS: {e}")


# --- 6. LINKEDIN POSTER APP ---

def app_linkedin_poster():
    st.title("Post to LinkedIn")
    st.markdown("Share a text post to your LinkedIn profile.")

    st.subheader("LinkedIn Credentials")
    st.info("You need to provide a valid Access Token from your LinkedIn Developer App.")
    access_token = st.text_input("Your LinkedIn Access Token", type="password")

    st.markdown("---")

    with st.form("linkedin_form"):
        message = st.text_area("Write your LinkedIn post content")
        submitted = st.form_submit_button("Post to LinkedIn")

        if submitted:
            if not access_token or not message:
                st.warning("Please provide your Access Token and a message to post.")
            else:
                with st.spinner("Posting to LinkedIn..."):
                    try:
                        headers = {
                            "Authorization": f"Bearer {access_token}",
                            "Content-Type": "application/json",
                            "X-Restli-Protocol-Version": "2.0.0",
                            "LinkedIn-Version": "202305" # Example version, good practice to include
                        }

                        # First, get the LinkedIn user ID
                        profile_response = requests.get("https://api.linkedin.com/v2/me", headers=headers)
                        profile_response.raise_for_status() # Will raise an error for non-200 responses
                        user_id = profile_response.json()['id']

                        # Then, create the post
                        post_data = {
                            "author": f"urn:li:person:{user_id}",
                            "lifecycleState": "PUBLISHED",
                            "specificContent": {
                                "com.linkedin.ugc.ShareContent": {
                                    "shareCommentary": { 
                                        "text": message
                                    },
                                    "shareMediaCategory": "NONE"
                                }
                            },
                            "visibility": {
                                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                            }
                        }

                        post_response = requests.post("https://api.linkedin.com/v2/ugcPosts", headers=headers, json=post_data)
                        post_response.raise_for_status()

                        st.success("Successfully posted to LinkedIn!")

                    except requests.exceptions.HTTPError as e:
                        st.error(f"Failed to post: An HTTP error occurred.")
                        st.json(e.response.json()) # Show detailed error from LinkedIn API
                    except Exception as e:
                        st.error(f"An unexpected error occurred: {e}")

# --- 7. HONEST AI CHATBOT APP ---

def app_honest_ai():
    st.title("The Honest AI Chatbot")
    st.markdown("Ask the AI anything. Based on your prompt, it's set up to be an echobot.")

    st.subheader("API Credentials")
    st.info("This tool uses the Gemini API via the OpenAI SDK wrapper.")
    api_key = st.text_input("Enter your API Key", type="password")

    st.markdown("---")

    with st.form("ai_form"):
        user_input = st.text_area("Your Message", placeholder="e.g., Hello, world!")
        submitted = st.form_submit_button("Ask Honest AI")

        if submitted:
            if not api_key:
                st.warning("Please enter your API key.")
            elif not user_input:
                st.warning("Please enter a message.")
            else:
                with st.spinner("Thinking..."):
                    try:
                        # Initialize the client with the provided key
                        client = OpenAI(
                            api_key=api_key,
                            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
                        )
                        
                        # Define the message payload
                        messages = [
                            {"role": "system", "content": "you are echobot AI assistant work like bot will then respond by sending the same message back to you"},
                            {"role": "user", "content": user_input}
                        ]

                        # Make the API call
                        response = client.chat.completions.create(
                            model="gemini-1.5-flash",
                            messages=messages
                        )
                        
                        ai_response = response.choices[0].message.content
                        st.success("Honest AI Responds:")
                        st.markdown(f"> {ai_response}")

                    except Exception as e:
                        st.error(f"An error occurred: {e}")


# --- 8. GOOGLE SEARCH APP ---

def app_Google_Search():
    st.title("Google Custom Search")
    st.markdown("Use the Google Custom Search API to find information on the web.")

    st.subheader("Google API Credentials")
    st.info("You'll need a Google API Key and a Custom Search Engine (CSE) ID.")
    api_key = st.text_input("Enter your Google API Key", type="password")
    cse_id = st.text_input("Enter your CSE ID", type="password")

    st.markdown("---")

    query = st.text_input("Enter your search query:")

    if st.button("Search"):
        if not all([api_key, cse_id, query]):
            st.warning("Please fill in all fields before searching.")
        else:
            with st.spinner("Searching..."):
                try:
                    service = build("customsearch", "v1", developerKey=api_key)
                    res = service.cse().list(q=query, cx=cse_id, num=10).execute()
                    results = res.get("items", [])
                    
                    if not results:
                        st.warning("No results found.")
                    else:
                        st.subheader("Top Search Results:")
                        for i, item in enumerate(results, 1):
                            title = item.get("title")
                            snippet = item.get("snippet")
                            link = item.get("link")
                            st.markdown(f"### {i}. [{title}]({link})")
                            st.write(snippet)
                            st.write("---")

                except HttpError as e:
                    st.error(f"An API error occurred: {e}")
                    st.json(e.content)
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")


# --- 9. PIXEL ART GENERATOR APP ---

def app_pixel_art_generator():
    st.title("Create Your Own Pixel Art")
    st.markdown("This app generates a colorful pixelated image based on your specifications.")

    with st.form("pixel_art_form"):
        st.subheader("Settings")
        width = st.slider("Image Width (pixels)", min_value=4, max_value=64, value=16)
        height = st.slider("Image Height (pixels)", min_value=4, max_value=64, value=16)
        scale = st.slider("Pixel Scale (zoom factor)", min_value=5, max_value=50, value=20)
        submitted = st.form_submit_button("Generate Image")

        if submitted:
            with st.spinner("Generating your pixel masterpiece..."):
                try:
                    # Create a new blank image
                    img = Image.new('RGB', (width, height))

                    # Fill the image with random colored pixels
                    for x in range(width):
                        for y in range(height):
                            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                            img.putpixel((x, y), color)
                    
                    # Scale up the image to make the pixels visible
                    scaled_img = img.resize((width * scale, height * scale), Image.NEAREST)

                    # Display the image in the app
                    st.image(scaled_img, caption="Your Generated Pixel Art", use_column_width=True)
                    
                    # Provide a download button
                    file_path = "pixel_art.png"
                    scaled_img.save(file_path)
                    with open(file_path, "rb") as file:
                        st.download_button(
                            label="Download Image",
                            data=file,
                            file_name="my_pixel_art.png",
                            mime="image/png"
                        )
                    st.success("Image generated! Use the button above to download it.")

                except Exception as e:
                    st.error(f"An error occurred: {e}")



# --- MAIN APP ROUTER ---


# A dictionary to map app names to their functions
APPS = {
    
    "Twilio Voice Call": app_twilio_call,
    "Gmail Sender": app_gmail_sender,
    "Instagram Poster": app_instagram_poster,
    "Twilio SMS Sender": app_twilio_sms,
    "LinkedIn Poster": app_linkedin_poster,
    "Honest AI Chatbot": app_honest_ai,
    "Google Search": app_Google_Search,
    "Pixel Art Generator": app_pixel_art_generator,
}

st.sidebar.title("Python Task")
st.sidebar.markdown("Select an application from the dropdown below.")
selection = st.sidebar.selectbox("Go to", list(APPS.keys()))

# Run the selected app
app_function = APPS[selection]
app_function()

st.sidebar.markdown("---")
st.sidebar.info(
    "This is a multi-app dashboard combining several automation tools. "
    "Created by combining multiple scripts."
)


