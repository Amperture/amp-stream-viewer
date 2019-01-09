'use strict'
const merge = require('webpack-merge')
const prodEnv = require('./prod.env')

module.exports = merge(prodEnv, {
  NODE_ENV: '"development"',
  API_URL: JSON.stringify(`http://localhost:5000/api`), 
  GOOGLE_AUTH_LINK: JSON.stringify(`http://localhost:5000/googleauth`), 
  GOOGLE_OAUTH_CLIENT_ID: JSON.stringify(`${process.env.GOOGLE_OAUTH_CLIENT_ID}`)
})
