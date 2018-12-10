// api/index.js
import axios from 'axios'

const API_URL = process.env.API_URL

export function fetchUserInfo(jwt){ // {{{
  return axios.post(`${API_URL}/userinfo`, {jwt:jwt})
} // }}}

export function authorizeUser(authCode){ // {{{
  console.log(authCode)
  return axios.post(`${API_URL}/auth`, {authCode: authCode})
} // }}}

export function homePageSearchText(searchText, sortMethod, jwt){ //{{{
  console.log(searchText, jwt)
  if(sortMethod == undefined){
    sortMethod = 'relevance';
  }
  return axios.post(`${API_URL}/searchyt`, 
    {
      searchText: searchText,
      sortMethod: sortMethod,
      jwt: jwt
    })
} //}}}
