# Amp's Stream Viewer
A stream viewing and Chat Analytics webapp for Youtube.

You can find a live demo of this app [here](https://vast-dusk-61702.herokuapp.com/)

## Built Using
* [Flask](http://flask.pocoo.org/) -- Python Microservices Framework.
  * Familiarity -- 2 years experience
* [Vue.JS](https://vuejs.org/) -- Javascript Framework
  * Familiarity -- None
* [Bulma](https://bulma.io/) -- CSS Framework
  * Familiarity -- None


## Getting Started
### Prerequisites
* `python` v3
  * `pip`
* NodeJS
  * `npm`
* PostgreSQL
* A registered Google API Application, see [here](https://console.developers.google.com/)

### Setup
#### Clone the repo and enter directory
```bash 
$ git clone git@github.com:Amperture/amp-stream-viewer.git
$ cd amp-stream-viewer
```
#### Required Environment Variables
Environment Variables can be placed in a file named `.flaskenv` in the project root directory for development.

```
FLASK_APP=sv.py`
BACKEND_URL # Typically `http://localhost:5000`
FRONTEND_URL # Typically `http://localhsot:8080`
FLASK_SECRET_KEY # Randomly generated ASCII String
DATABASE_URL # `postgresql+psycopg2://<user>:<pass>@<IP>/<database>`
FLASK_DEBUG #1/0
```
* Google App Credentials
```
GOOGLE_OAUTH_CLIENT_ID
GOOGLE_OAUTH_CLIENT_SECRET
GOOGLE_OAUTH_REDIRECT_URI
GOOGLE_OAUTH_AUTH_URI
GOOGLE_OAUTH_TOKEN_URI
GOOGLE_USER_INFO
```
#### Setup Backend
```bash
$ python3 -m venv venv # Create Virtual Environment
$ source venv/bin/activate 
(venv) $ pip install -r requirements.txt

# At this point you'll want to make sure you have your PostgreSQL server is up
# and running and you have your DATABASE_URL environment variable is populated.
(venv) $ flask db init
(venv) $ flask db migrate 
(venv) $ flask db upgrade

(venv) $ flask run # Run Development Server
```
#### Setup Frontend
```bash
$ npm i       # Install Dependencies
$ npm run dev # Run Development Server

# Navigate in your browser of choice to the url provided.
```
