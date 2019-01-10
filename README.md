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
## Design
This project was taken on as a challenge test project found [here](https://gist.github.com/osamakhn/aeed06830fbafa2ff9fd31a8326fec0d)
to better understand front-end development and the Google API libraries, 
especially the Youtube Data and Youtube Live Streaming APIs. A few key decisions
were made in the design to facilitate functionality.

### PostgreSQL
PostgreSQL was chosen for its support of `ON_CONFLICT` parameters for 
inserts into upserts in the `SQLAlchemy` library.

This was done especially for the case of adding a `ChatterLog` who had 
changed their displayed username or avatar.`

### Custom Chat Table
Theoretically the chat from youtube could simply be embedded into the viewing 
webpage, but since chat must be logged locally to the backend server, it 
becomes ideal that all chat be routed through the backend server regardless.

This would create a scenario where chat can only be logged if someone is 
actively watching a stream while using the app, but given the `Kevin` user 
persona, that assumption was reasonable. 

An alternative method, given more resources could be to log all streams at time
of search using multithreaded process in the backend server.

### Front Page Search
The landing page of the app *when the user is logged in* will show a default
list of streams to the user. This list follows the following algorithm:
* If the user has never executed a search manually, search using an empty string.
* Otherwise, repeat the last search the user performed.

This assumption was made on the discovery that using an empty string in the Youtube
Search API will return what looks to be curated suggestions directly from 
Youtube. This was tested with three users initially and seems to be the case.

