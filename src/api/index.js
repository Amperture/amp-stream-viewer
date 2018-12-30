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
export function fetchStreamInfo(videoID, jwt){ //{{{
  //console.log("GRABBING VIDEO CHAT ID WITH PARAMETERS")
  //console.log(videoID, jwt)
  return axios.post(`${API_URL}/getstreaminfo`, {
      videoID: videoID,
      jwt: jwt
    })
} //}}}
export function fetchChatMessages( // {{{
  chatID, 
  videoID, 
  chatNextPageToken, 
  jwt ){ 
  //console.log(chatID, chatNextPageToken, jwt)
  return axios.post(`${API_URL}/getchatmsgs`, {
      chatID            : chatID,
      videoID           : videoID,
      chatNextPageToken : chatNextPageToken,
      jwt               : jwt
    })
} // }}}
export function sendChatMessage( // {{{
  chatID, 
  messageText, 
  jwt ){ 
  //console.log(chatID, chatNextPageToken, jwt)
  return axios.post(`${API_URL}/sendchatmsg`, {
      chatID: chatID,
      messageText: messageText,
      jwt: jwt
    })
} // }}}
export function fetchStreamStats( // {{{
  videoID, 
  jwt ){ 
  //console.log(videoID, jwt)
  return axios.post(`${API_URL}/getstreamstats`, {
      videoID: videoID,
      jwt: jwt
    })
} // }}}
export function fetchErrorTest(){ // {{{
  return axios.get(`${API_URL}/errortest`)
} // }}}
