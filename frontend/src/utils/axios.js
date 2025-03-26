
import axios from 'axios'
import { API_BASE_URL } from './constants';

const apiInstance = axios.create({
    baseURL: API_BASE_URL,
    timeout: 10000,                                      // this means that after 10 seconds, if now value has been returned. Then it will automatically terminate the fetch call
    headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
    }
});


export default apiInstance


// Example of what this does for us below. Also it is suggested to build the code this way so we can specify a timeout time and dont have to go back and replace all of the fetches later if want to add this
// apiInstance.get(`get-studnet-course`)


// If we dont want to write this file, we can still use the below:
// axios.get(`get-student-course`)




