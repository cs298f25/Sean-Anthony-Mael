import google.generativeai as genai

# Configure the API key (you'll need to set this from an environment variable)
genai.configure(api_key="AIzaSyBT1wi1JXhD_eahUdi3Z1MXjiFHOcSv04E")

model = genai.GenerativeModel('gemini-2.5-flash')

response = model.generate_content("Give me top 5 songs for today's weather in Bethlehem, PA")

print(response.text)