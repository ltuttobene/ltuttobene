from flask import Flask, render_template, request, redirect, url_for, make_response
import smtplib
from email.message import EmailMessage
import os
import os.path
from google.oauth2 import service_account
import gspread
import pandas as pd
import json

app = Flask(__name__)

# Path to your credential JSON file
credential_file = os.path.join(
    #os.getcwd(), "credentials/spartan-soccer-2db8e2aa941f.json"
    os.getcwd(), "credentials/magic-project-401621-5b857db126c0.json"
    
)

# Load credentials from the JSON file
credentials = service_account.Credentials.from_service_account_file(
    credential_file,
    scopes=[
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ],
)
# Create a client to interact with Google Sheets API
client = gspread.authorize(credentials)

# Open the Google Spreadsheet
spreadsheet = client.open("Magic")

# Select the specific sheet within the spreadsheet
sheet = spreadsheet.sheet1  # Assuming the data is on the first sheet

# Fetch all the values from the sheet
data = sheet.get_all_values()

# Create a DataFrame using the fetched data
df = pd.DataFrame(data[1:], columns=data[0])



#Prepare risultati data 
#Open the Google Spreadsheet
spreadsheet = client.open("Magic")

# Select the specific sheet within the spreadsheet
sheet2 = spreadsheet.worksheet("sheet2")

# Fetch all the values from the sheet
data2 = sheet2.get_all_values()

# Create a DataFrame using the fetched data
df2 = pd.DataFrame(data2[1:], columns=data2[0])

########## POLL VOTE CODE ##########
if not os.path.exists("polls.csv"):
    structure = {
        "pid": [], 
        "poll": [],
        "option1": [],
        "option2": [],
        "option3": [],
        "option4": [],
        "option5": [],
        "option6": [],
        "option7": [],
        "option8": [],
        "option9": [],
        "option10": [],
        "votes1": [],
        "votes2": [],
        "votes3": [],
        "votes4": [],
        "votes5": [],
        "votes6": [],
        "votes7": [],
        "votes8": [],
        "votes9": [],
        "votes10": [],
    }

    pd.DataFrame(structure).set_index("pid").to_csv("polls.csv")

polls_df = pd.read_csv("polls.csv").set_index("pid")

# Define a route to render the players page
@app.route("/players")
def players():
    # Convert DataFrame to list of dictionaries
    player_data = df.to_dict(orient="records")

    
    # Render the players.html template and pass the player data
    return render_template("players.html", players=player_data)


# Define a route to render the risultati page
@app.route("/risultati")
def risultati():
    # Convert DataFrame to list of dictionaries
    risultati_data = df2.to_dict(orient="records")

    
    # Render the risultati.html template and pass the risultati data
    return render_template("risultati.html", risultati=risultati_data)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/calendar")
def calendar():
    # Open the Google Spreadsheet
    spreadsheet = client.open('Magic')  # Replace 'spartancalendar' with the actual title of your calendar spreadsheet

    # Select the specific sheet within the spreadsheet by its title
    sheet_title2 = 'Sheet3'  # Replace 'Sheet1' with the title of your sheet
    sheet = spreadsheet.worksheet(sheet_title2)

    # Fetch all the values from the sheet
    data = sheet.get_all_values()

    # Create a DataFrame using the fetched data
    df = pd.DataFrame(data[1:], columns=data[0])
    # Fetch events from Google Sheets and convert them to a list of dictionaries
    events = [
        {
            "title": row["Event Title"],
            "start": row["Start Date"],
            "end": row["End Date"],
            "color": row["Color"]  # You can add a "color" column in your Google Sheet to specify the event color
        }
        for row in sheet.get_all_records()
    ]
    # Convert the events data to a JSON string
    events_json = json.dumps(events)
    # Add this line to check the events_json content
    # print(events_json)  

    
    return render_template("calendar.html", events_json=events_json)

@app.route("/votazione")
def votazione():
    return render_template("polls.html", polls= polls_df)


@app.route("/votazione/polls/<pid>")
def polls(pid):
    poll = polls_df.loc[int(pid)]
    return render_template("show_poll.html", poll=poll)

@app.route("/votazione/polls", methods=[ "GET", "POST"])
def create_poll():
    if request.method == "GET":
        return render_template("new_poll.html")
    elif request.method == "POST":
        poll = request.form['poll']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        option5 = request.form['option5']
        option6 = request.form['option6']
        option7 = request.form['option7']
        option8 = request.form['option8']
        option9 = request.form['option9']
        option10 = request.form['option10']
        polls_df.loc[max(polls_df.index.values) + 1] = [poll, option1,option2, option3, option4, option5, option6, option7, option8, option9, option10,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        polls_df.to_csv("polls.csv")
        return redirect(url_for("votazione"))

@app.route("/votazione/vote/<pid>/<option>")
def vote(pid, option):
    if request.cookies.get(f"vote_{id}_cookie") is None:
        polls_df.at[int(pid), "votes"+str(option)] += 1
        polls_df.to_csv("polls.csv")
        response = make_response(redirect(url_for("polls", pid=pid)))
        response.set_cookie(f"vote_{id}_cookie", str(option))
        return response
    else:
        return "Cannot vote more than once!"
    #return redirect(url_for("polls", pid=pid))


########## MAIN ##########
if __name__ == "__main__":
    app.run()
