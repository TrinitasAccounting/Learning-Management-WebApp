
import axios from 'axios'
import { API_BASE_URL } from './constants';

// const apiInstance = axios.create({
//     baseURL: API_BASE_URL,
//     timeout: 10000,                                      // this means that after 10 seconds, if now value has been returned. Then it will automatically terminate the fetch call
//     headers: {
//         'Content-Type': 'application/json',
//         Accept: 'application/json',
//     }
// });


// export default apiInstance


// Example of what this does for us below. Also it is suggested to build the code this way so we can specify a timeout time and dont have to go back and replace all of the fetches later if want to add this
// apiInstance.get(`get-student-course`)


// If we dont want to write this file, we can still use the below:
// axios.get(`get-student-course`)




import { setAuthUser, getRefreshedToken, isAccessTokenExpired } from "./auth";
import Cookies from "js-cookie";


// Create an Axios instance with default settings
const apiInstance = axios.create({
    baseURL: "http://127.0.0.1:8000/api/v1/",
    timeout: 10000,
    headers: {
        "Content-Type": "application/json",
    },
});

// Request interceptor for adding authentication token if available
apiInstance.interceptors.request.use(
    async (config) => {
        const accessToken = Cookies.get("access_token"); // Updated cookie names for consistency with your app

        // If the access token exists, add it to the Authorization header
        if (accessToken) {
            config.headers.Authorization = `Bearer ${accessToken}`;
        }

        // If the access token is expired, attempt to refresh it
        if (isAccessTokenExpired(accessToken)) {
            const refreshToken = Cookies.get("refresh_token"); // Updated for consistency
            if (refreshToken) {
                try {
                    const response = await getRefreshedToken(refreshToken);

                    // Update the token cookies and headers
                    setAuthUser(response.data.access, response.data.refresh);
                    config.headers.Authorization = `Bearer ${response.data.access}`;
                } catch (error) {
                    // Handle refresh token failure (e.g., log out user or show an error message)
                    console.error("Token refresh failed:", error);
                }
            }
        }

        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor for handling errors
apiInstance.interceptors.response.use(
    (response) => response,
    (error) => {
        // Handle specific error cases if needed
        if (error.response && error.response.status === 401) {
            // Handle unauthorized errors (e.g., redirect to login)
            console.error("Unauthorized access - you may need to log in:", error);
        }

        return Promise.reject(error);
    }
);

export default apiInstance;









