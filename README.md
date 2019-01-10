# Amp's Stream Viewer
A stream viewing and Chat Analytics webapp for Youtube.

You can find a live demo of this app [here](https://vast-dusk-61702.herokuapp.com/)

## Getting Started

### Prerequisites
* `python` v3
  * `pip`
* NodeJS
  * `npm`
* PostgreSQL
* A registered Google API Application, see [here](https://console.developers.google.com/)

### Setup
* Clone the repo and enter directory
  1. `$ git clone git@github.com:Amperture/amp-stream-viewer.git`
  2. `$ cd amp-stream-viewer`

* Installing depdency packages for Frontend
  1. `$ npm i`

* Setup for Virtual Environment For Python and Install Dependencies for Backend
  1. `$ python3 -m venv venv`
  2. `$ source venv/bin/activate`
  3. `$ pip install -r requirements.txt`

* Required Environment Variables
  * `FLASK_APP=sv.py`
  * Google App Credentials
    * `GOOGLE_OAUTH_CLIENT_ID`
    * `GOOGLE_OAUTH_CLIENT_SECRET`
    * `GOOGLE_OAUTH_REDIRECT_URI`
    * `GOOGLE_OAUTH_AUTH_URI`
    * `GOOGLE_OAUTH_TOKEN_URI`
    * `GOOGLE_USER_INFO`
  * `BACKEND_URL`: Typically `http://localhost:5000`
  * `FRONTEND_URL`: Typically `http://localhsot:8080`
  * `FLASK_SECRET_KEY`: Randomly generated ASCII String
  * `DATABASE_URL`: Typically `postgresql+psycopg2://<user>:<pass>@<IP>/<database>`
  * `FLASK_DEBUG`: 1 or 0
  * Environment Variables can be placed in a file named `.flaskenv` in the project root directory.


## Design Decisions
A general theme 
