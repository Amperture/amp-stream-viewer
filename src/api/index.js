// api/index.js
import axios from 'axios'

const API_URL = process.env.API_URL

export function fetchUserInfo(){ // {{{
  let jwt = localStorage.getItem('jwt')
  return axios.get(`${API_URL}/auth`, 
    {
      headers: {
        Authorization : jwt
      }
    }
  )
} // }}}
export function authorizeUser(authCode){ // {{{
  console.log(authCode)
  return axios.post(`${API_URL}/auth`, {authCode: authCode})
} // }}}
export function fetchYoutubeStreamSearch(searchText, sortMethod){ //{{{
  let jwt = localStorage.getItem('jwt')
  if(sortMethod == undefined){
    sortMethod = 'relevance';
  }
  return axios.get(`${API_URL}/youtube/search`, 
    {
      params: {
        searchText: searchText,
        sortMethod: sortMethod
      },
      headers: {
        'Authorization' : jwt
      }
    })
} //}}}
export function fetchStreamInfo(videoID){ //{{{
  let jwt = localStorage.getItem('jwt')
  return axios.get(`${API_URL}/youtube/stream`, 
    {
      params: {
        videoID: videoID
      },
      headers: {
        'Authorization' : jwt
      }
    })
} //}}}
export function fetchChatMessages( // {{{
  chatID, 
  videoID, 
  chatNextPageToken){ 

  let jwt = localStorage.getItem('jwt')
  return axios.get(`${API_URL}/chat/youtube`, 
    {
      params  : {
        chatID            : chatID,
        videoID           : videoID,
        chatNextPageToken : chatNextPageToken, 

      },
      headers: {
        'Authorization' : jwt
      }
    }
  )
}

// }}}
export function sendChatMessage( // {{{
  chatID, 
  messageText){
  let jwt = localStorage.getItem('jwt')
  return axios.post(`${API_URL}/chat/youtube`, {
      chatID: chatID,
      messageText: messageText
    },
    {
      headers: {
        'Authorization' : jwt
      }
    })
} // }}}
export function fetchStreamStats( // {{{
  videoID, 
  perPage, 
  page, 
  orderBy, 
  filtSponsors,
  filtMods, 
  chatterNameSearch){ 

  let jwt = localStorage.getItem('jwt')
  return axios.get(`${API_URL}/chat/youtube/stats`, 
    {
      params: {
        videoID: videoID,
        perPage: perPage,
        page: page - 1,  // Show pages from 1, but send from 0
        orderBy: orderBy,
        chatterNameSearch: chatterNameSearch,
        filtSponsors: filtSponsors,
        filtMods: filtMods
      },
      headers: {
        'Authorization' : jwt
      }
    }
  )
}

// }}}
export function fetchErrorTest(){ // {{{
  let jwt = localStorage.getItem('jwt')
  return axios.get(
    `${API_URL}/errortest`,
    {
      headers  : {
        Authorization : jwt
      }
    }
  )
} // }}}
export function fetchUserChatLog(videoID, authorID, pageNum, perPage){ // {{{
  let jwt = localStorage.getItem('jwt')
  return axios.get(
    `${API_URL}/chat/youtube/log`,
    {
      params   : {
        videoID         : videoID,
        authorID        : authorID, 
        resultsPerPage  : perPage,
        pageNum         : pageNum - 1 ,
        logMethod       : 'authorID'
      },
      headers  : {
        Authorization : jwt
      }
    }
  )
} // }}}
export function fetchContextChatLog(videoID, msgID, pageNum, perPage){ // {{{
  let jwt = localStorage.getItem('jwt')
  return axios.get(
    `${API_URL}/chat/youtube/log`,
    {
      params   : {
        videoID         : videoID,
        resultsPerPage  : perPage,
        pageNum         : pageNum - 1,
        msgID           : msgID, 
        logMethod       : 'msgID'
      },
      headers  : {
        Authorization : jwt
      }
    }
  )
} // }}}
