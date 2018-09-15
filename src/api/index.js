// api/index.js
import axios from 'axios'

const API_URL = process.env.API_URL

export function fetchUserInfo(){
  return axios.get(`${API_URL}/userinfo`)
}
