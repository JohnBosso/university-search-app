# USA University Search App

## Video Demo
https://youtu.be/cfRDwjj5V4Y

## Project Description
The **USA University Search App** allows users to search for universities based on specific criteria. Users must register and log in to access the web app. Once logged in, they can:
- Search for a specific university by name to view relevant details.
- Filter universities based on their preferences, such as degree type, program, and state.

## Folder & File Structure

### Templates Folder
This folder contains all HTML files used in the web application.

#### `layout.html`
This file defines the base layout for all pages. It ensures consistency across the web app and dynamically adjusts navigation links based on the user's authentication status.

#### `error.html`
Displays an error message and image when a specific condition is not met.

#### `register.html`
Provides a registration form with fields for username, password, confirm password, and email address.

#### `login.html`
The first interface users see upon visiting the web app. It requires users to enter their credentials. Successful login redirects to `junction.html`; otherwise, an error message is displayed.

#### `junction.html`
The main dashboard users see after logging in. It contains links to the two search options.

#### `sch_home.html`
Allows users to search for universities by name. It includes an input field for entering the university name and a submit button.

#### `school.html`
Displays university details such as acceptance rate and degree programs. Degree information is presented in a table format.

#### `filter.html`
Enables users to filter universities based on degree type, state, and program name. The form includes dropdowns and input fields for user selection.

#### `fresult.html`
Displays a list of universities that match the selected filters, along with relevant details such as acceptance rates.

### Static Folder
Contains stylesheets and helper functions.

#### `style.css`
Defines the visual styling of the web app, including text formatting, tables, buttons, and containers.

### Helper Functions

#### `helper.py`
Contains utility functions for formatting numerical data:
- `usd(value)`: Formats currency values in US dollars.
- `percentage(value)`: Converts float values to percentage format.
- `number(value)`: Formats numerical values with commas for better readability.

### `app.py`
This is a Flask-based web application that allows users to search for universities in the United States. The app provides details like tuition fees, acceptance rates, and degree programs using data from the U.S. Department of Education's College Scorecard API.

### **Functions in `app.py`**

#### **`register`**
- Accepts the `POST` method at the `/register` endpoint.
- Takes user input and saves it in the **users** table.

#### **`login`**
- Accepts the `POST` method at the `/login` endpoint.
- Checks if the user exists in the database and grants access to the web app by storing user sessions.

#### **`junction`**
- Accepts the `POST` method at the `/junction` endpoint.
- Displays links to the two search types for the user.

#### **`home`**
- Accepts the `POST` method at the `/home` endpoint.
- Requests university data from the **College Scorecard API** using the university name as a filter and returns the details to the user.

#### **`filter_results`**
- Accepts the `POST` method at the `/filter` endpoint.
- Requests university data from the **College Scorecard API**, filtering by **degree type, U.S. states, and program of study**, and returns the details to the user.

#### **`logout`**
- Clears the user session and redirects to the login page.


### **Technologies Used**
- **Flask**: Web framework for Python  
- **Flask-MySQLdb**: MySQL integration for Flask  
- **Flask-SQLAlchemy**: ORM for database interactions  
- **Werkzeug**: Password hashing and authentication  
- **Requests**: API interaction with College Scorecard  
- **Jinja2**: Template rendering engine  
- **Bootstrap**: Frontend styling framework  

### **Installation**
#### **Clone the repository:**
```bash
git clone https://github.com/your-repo/university-search.git


### **MySQL Database**  
I am using an online database because the web app is deployed after pushing it to GitHub.  
Set up your MySQL database and update:  

```python
app.config["SQLALCHEMY_DATABASE_URI"] = "your-database-uri"


#### Run database migrations:
flask db init
flask db migrate -m "Initial migration."
flask db upgrade

#### API Integration
The application uses the College Scorecard API from data.gov to fetch university data. To use this API, obtain an API key from data.gov and update API_KEY in app.py.

#### Database Schema

### **Table: `university`**
1. `userid` (`INT, PRIMARY KEY, AUTO_INCREMENT`)
2. `username` (`VARCHAR, UNIQUE`)
3. `email` (`VARCHAR, UNIQUE`)
4. `password` (`VARCHAR, HASHED`)



### **Important Notes**
1. All input requests are made via `POST`.  
2. User input is always validated; if a required value is missing, an error message is displayed.  
3. Passwords are hashed.  
4. Initially planned to use buttons to display key information like the acceptance rate but opted for containers for flexibility.  
5. The app is deployed and accessible to everyone.  
6. **Alwaysdata.com** is used as the online database system for storing user information.  
7. **Render.com** is used to deploy the web app.  
8. The error image (*sad cat*) is linked from an online source.  

#### `layout.html`

## How to Use
1. Register for an account.
2. Log in to access the dashboard (`junction.html`).
3. Choose between:
   - Searching for a specific university (`sch_home.html`).
   - Filtering universities based on criteria (`filter.html`).
4. View detailed results on `school.html` or `fresult.html`.
