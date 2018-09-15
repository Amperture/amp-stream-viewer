// api/index.js
import axios from 'axios'

const API_URL = 'http://localhost:5000/api'

export function fetchUserInfo(){
  return axios.get(`${API_URL}/userinfo`)
}
