'use strict'
module.exports = {
  NODE_ENV: '"production"',
  API_URL: JSON.stringify(`${process.env.BACKEND_URL}/api`), 
  GOOGLE_AUTH_LINK: JSON.stringify(`${process.env.BACKEND_URL}/googleauth`), 
  GOOGLE_OAUTH_CLIENT_ID: JSON.stringify(`${process.env.GOOGLE_OAUTH_CLIENT_ID}`)
}
