import html
from quart import Quart, request, render_template_string
from openai import OpenAI
import json
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()
import time

import logging

# Set up logging to display errors
logging.basicConfig(level=logging.DEBUG)

# Initialize Quart app
app = Quart(__name__)
# HTML template for the page
html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Musical Matchmaker</title>
    <style>
    html, body {font-family: sans-serif;
font-size:1.5em; 
color: #00008B;
margin: 0;
background: rgb(204,204,255);
}
form {
max-width: 700px;
margin: 0 auto;
padding: 15px;
border: 10px solid black;
text-align: center;
}
h1, h2, h3 {
text-align: center;
}
form {
max-width: 480px;
margin: 0 auto;
padding: 16px;
border: 1px solid black;
}
h2 {
text-align: center;
}
p{
    white-space: pre-wrap;
    word-break: normal;
    margin: 0 150px;
    }
    #user_input{
    margin-top:20px;
    padding:15px 0;
    text-align: center;}
pre {
    white-space: pre-wrap;
    word-break: normal;
    margin: 0 120px;
    border: 1px solid black;
    padding: 16px;
    }
    body {
	margin: 0;
	padding: 0;
   
}

.container {
	width: 200px;
	height: 100px;
	padding-top: 100px;
	margin: 0 auto;
}
   
    button{
    background-color: #00008B;
    color: #fff;
    border: .2px #00008B;
    padding: 2px;
    cursor: pointer;
    font-size: 1em;
    border-radius: 4px;
    transition: background-color 0.3s;}
   </style>  
</head>
<body>
    <h1>Musical Matchmaker</h1>
    <form method="POST" action="/submit">
    <label for="options">What type of show would you like to see?:</label><br>

    <select name="options" id="options">
        <option value="serious">Serious</option>
        <option value="funny">Funny</option>
        <option value="history">History</option>
        <option value="disney">Disney</option>
        <option value="classic">Classic</option>
        <option value="family">Family</option>
        <option value="adventure">Adventure</option>
        <option value="holiday">Holiday</option>
    </select>
    <button type="submit">Here We Go!</button>
</form>
    {% if assistant_reply %}
    <h2>Musical Matchmaker's Recommendations:</h2>
    <pre>{{ assistant_reply }}</pre>
    {% endif %}
    
</body>
</html>
'''

@app.route('/')
async def index():
    # Render the initial HTML page with no response yet
    return await render_template_string(html_template)
@app.route('/submit', methods=['POST'])
async def submit():
    # Retrieve the value from the select menu
    data = await request.form
    user_input = data.get('options')

    # Interact with OpenAI API
    assistant = client.beta.assistants.create(
        name="trivia master",
        description="You are a Broadway musical master. You know everything about the current shows that are running on Broadway and the stories of all movie musicals. Based on the words, themes, or ideas provided by the user, you will offer recommendations of Broadway shows and/or movie musicals that match. Do not repeat recommendations",
        model="gpt-4-turbo",
        tools=[{"type": "code_interpreter"}]
    )
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": "Create a list of 3 Broadway musicals or movie musicals with information on how to buy tickets or where one could watch the movie based on the value of user_input."
            }
        ]
    )
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input
    )
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions=""
    )
    while run.status != "completed":
        time.sleep(5)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        print(f"\t\t{run}")

    if run.status == 'completed':
        messages = client.beta.threads.messages.list(
        thread_id=thread.id).model_dump_json()

    # Extract the assistant's response
    json_data = json.loads(messages)
    values = []
    for item in json_data['data']:
        values.append(item['content'][0]['text']['value'])
        values = values.pop()
        assistant_response = values
        # Render the HTML page with the ChatGPT response
        return await render_template_string(html_template, assistant_reply=assistant_response)

if __name__ == '__main__':
    app.run(debug=True)