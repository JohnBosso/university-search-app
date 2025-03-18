from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash, generate_password_hash
import requests
import json

from helper import usd, percentage, number


app = Flask(__name__)
app.jinja_env.auto_reload = True
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd
app.jinja_env.filters["percentage"] = percentage
app.jinja_env.filters["number"] = number

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config['MYSQL_HOST'] = 'localhost' 
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'MonkeyDLuffy8.'
app.config['MYSQL_DB'] = 'db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        
        name = request.form.get('username')
        password = request.form.get('password')
        
        if not name:
            return render_template('error.html', sorry='Name field required')
        if not isinstance(name, str):
            return render_template('error.html', sorry='Name must be a string')

        cur.execute('SELECT * FROM users')
        namedict = cur.fetchall()
        length = len(namedict) 

        if length < 1:
            return render_template('error.html', sorry='Name is not registered')

        names = [namedict[list]['username'] for list in range(length)]

        if name not in names:
            return render_template('error.html', sorry='Name is not registered')
        
        if not password:
            return render_template('error.html', sorry='Password field required')
        
        cur.execute('SELECT userpassword FROM users WHERE username = %s', (name,))
        passwords = cur.fetchall()
        
        if len(passwords) != 1 or not check_password_hash(passwords[0]['userpassword'], password):
            return render_template('error.html', sorry='Password is not registered')
        
        cur.execute('SELECT userid FROM users WHERE username = %s', (name,))
        user_id = cur.fetchall()

        session['userid'] = user_id[0]['userid']

        return redirect('/junction')

    else:
        return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        cur = mysql.connection.cursor()

        name = request.form.get('username')
        mypassword = request.form.get('mypassword')
        c_password = request.form.get('cpassword')
        mails = request.form.get('mails')

        if not name or not mypassword or not c_password or not mails:
            return render_template('error.html', sorry='All fields required')
        
        try:
            name = int(name)
            if type(name) is not str:
                return render_template('error.html', sorry='Name field must be text')
        except ValueError:
            if mypassword != c_password:
                return render_template('error.html', sorry='Passwords do not match')

        
            if not mails.endswith('@gmail.com'):
                return render_template('error.html', sorry='Only gmail required')
        
            hash = generate_password_hash(mypassword, method='scrypt', salt_length=16)

            cur.execute('INSERT INTO users(username, gmail, userpassword) VALUES (%s, %s, %s)', (name, mails, hash))
            cur.connection.commit()
        
            return redirect('/')
        
    else:
        return render_template('register.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        name = request.form.get('sch_name')
        corr_name = name.title()

        if not name:
            return render_template('error.html', sorry='School Name required')

        # Your API key from data.gov
        API_KEY = "3daA2AJdE6VmviPSGOUpXOHVjSbCv2vrLbvygGAE"

        # API Endpoint for fetching university data
        url = f"https://api.data.gov/ed/collegescorecard/v1/schools?school.name={name}&_per_page=1&api_key={API_KEY}"

        # Make the request
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
        
            if not data["results"]:  # ✅ Check if API found the school
                return render_template('error.html', sorry='School not found in API')
            
            # Print the first 10 universities
            school = data["results"][0]

            names = school['latest']["school"]["name"]
            proper_names = names.title()
            city = school['latest']["school"]["city"]
            state = school['latest']["school"]["state"]
            website = school['latest']["school"].get("website", "N/A")  # Some universities may not have a website listed
            acceptance_rate = school['latest']['admissions']['admission_rate']['overall']
            num_oftest = school['latest']['admissions']['test_requirements']
            book_cost = school['latest']['cost']['booksupply']
            tuition = school['latest']['cost']['tuition']
            room_cost = school['latest']['cost']['roomboard']
            pell_grant_rate = school['latest']['aid']['pell_grant_rate']
            
            programs = school['latest'].get('programs',{}).get('cip_4_digit', [])
            degrees = [{'title': program['title'], 'degree':program['credential']['title']} for program in programs]
            
            demo = school['latest']['student']
            demographic = {'population': demo.get('size', 0), 'grad_student': demo.get('grad_students', 0), 'men': demo.get('demographics', {}).get('men', 0), 'women': demo.get('demographics', {}).get('women', 0)}
        
            return render_template('school.html', sch_names = proper_names, cities = city, states = state, sites = website,
                                   accepts = acceptance_rate, tests = num_oftest, books = book_cost, fees = tuition, rooms = room_cost,
                                grants = pell_grant_rate,  degree = degrees, demographics = demographic)
        
        else:
            return render_template('error.html', sorry='Failed to fetch data')

        
        cur.execute('SELECT * FROM schools WHERE sch_name LIKE %s', (f"%{corr_name}%",))
        schools = cur.fetchall()

    else:
        return render_template('sch_home.html')


@app.route("/junction", methods=['GET', 'POST'])
def junction():
    if request.method == 'POST':
        if request.form.get('school_search') == 'home':
            return render_template('sch_home.html')
        elif request.form.get('filter_search') == 'filter':
            return render_template('filter.html')
    else:
        return render_template('junction.html')

@app.route('/filter', methods=['POST', 'GET'])
def filter_results():
    if request.method == 'POST':
        degree_type = request.form.get('degree_type')
        state = request.form.get('state')
        degree_name = request.form.get('degree_name')

        if not degree_type or not state or not degree_name:
            return render_template('error.html', sorry='All fields are required')

        us_state = state.title()

        us_states = {
                        "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
                        "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA",
                        "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
                        "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
                        "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO",
                        "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ",
                        "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
                        "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
                        "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
                        "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"
                    }
        if us_state not in us_states.keys():
            return render_template('error.html', sorry='Enter Valid US State')
        
        states = us_states[us_state]

        degree = int(degree_type)
        API_KEY = "3daA2AJdE6VmviPSGOUpXOHVjSbCv2vrLbvygGAE"
        base_url = "https://api.data.gov/ed/collegescorecard/v1/schools?"

        word = degree_name.lower()  # Fixes unnecessary period
        schools = []
        page = 0  # Start from page 0
        max_pages = 5

        while page < max_pages:
            url = f"{base_url}school.degrees_awarded.predominant={degree}&_per_page=100&_page={page}&school.state={states.upper()}&api_key={API_KEY}"

            try:
                response = requests.get(url)
                response.raise_for_status()  # Ensure request was successful
                data = response.json()
            except requests.exceptions.RequestException as e:
                return render_template('error.html', sorry=f"API request failed: {e}")
            except ValueError:
                return render_template('error.html', sorry="Invalid response from API")

            if page == 0:
                print("Total Results Available:", data.get("metadata", {}).get("total", 0))

            if not data.get("results"):
                break

            new_programs = []
            for j in data["results"]:
                titles = [title.get('title', 'N/A').lower() for title in j.get("latest", {}).get("programs", {}).get("cip_4_digit", [])]
                acceptance_rate = j.get("latest", {}).get("admissions", {}).get("admission_rate", {}).get("overall", "N/A")
                school_name = j.get("latest", {}).get("school", {}).get("name", "Unknown School").title()
                city = j.get("latest", {}).get("school", {}).get("city", "Unknown City")
                state_abbr = j.get("latest", {}).get("school", {}).get("state", "Unknown State")
                in_state_tuition = j.get("latest", {}).get("cost", {}).get("tuition", {}).get("in_state", "N/A")
                out_of_state_tuition = j.get("latest", {}).get("cost", {}).get("tuition", {}).get("out_of_state", "N/A")

                new_programs.append({
                    'title': titles,
                    'acceptance_rate': acceptance_rate,
                    'school_name': school_name,
                    'city': city,
                    'state': state_abbr,
                    'in_state_tuition': in_state_tuition,
                    'out_of_state_tuition': out_of_state_tuition
                })

            # Check if the desired degree name exists in any program
            matching_programs = [
                {
                    **prog,  # Keep all other fields
                    'title': {title for title in prog['title'] if word in title}  # Keep only matching titles
                }
                for prog in new_programs if any(word in title for title in (prog['title'] or []))
            ]

            for match in matching_programs:
                school_info = {
                    "name": match['school_name'],
                    "city": match['city'],
                    "state": match['state'],
                    "acceptance_rate": match['acceptance_rate'],
                    "in_state_tuition": match['in_state_tuition'],
                    "out_of_state_tuition": match['out_of_state_tuition'],
                    'titles': match['title']
                }
                schools.append(school_info)

            page += 1  # Move to the next page

        return render_template('fresult.html', schools=schools)
    else:
        us_states = {
                        "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
                        "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA",
                        "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
                        "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
                        "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO",
                        "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ",
                        "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
                        "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
                        "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
                        "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"
                    }
        return render_template('filter.html',  us_states = us_states.keys())

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)  
    # school.name, school.address, school.faculty_salary, peps_ownership, school.school_url, school.accreditor, 
    # school.ft_faculty_rate, school.price_calculator_url, school.degrees_awarded, school.tuition_revenue_per_fte, school.student[size], 
    # school.student[grad_students], school.student,