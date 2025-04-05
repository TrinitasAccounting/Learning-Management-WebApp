
import axios from 'axios'
import { getRefreshedToken, isAccessTokenExpired, setAuthUser } from './auth'
import { API_BASE_URL } from './constants'
import Cookies from 'js-cookie';



const useAxios = () => {
    const accessToken = Cookies.get("access_token");
    const refreshToken = Cookies.get("refresh_token");

    // Django when accessing private routes, requires you pass an access token in the header. This useAxios will do this automatically for us
    const axiosInstance = axios.create({
        baseURL: API_BASE_URL,
        headers: { Authorization: `Bearer ${accessToken}` }
    });

    // these interceptors seem to be adding additional abilities for when we fetch from protected routes or something
    axiosInstance.interceptors.request.use(async (req) => {
        if (!isAccessTokenExpired) {
            return req;
        }

        const response = await getRefreshedToken(refreshToken)        // calling this function from our utils auth file
        setAuthUser(response.access, response.refresh);          // another utils auth function. Passing in the response returned jwt tokens from running getRefreshedToken
        req.headers.Authorization = `Bearer ${response.data?.access}`       // we are grabbing the new access token from the response, and sending it along side the request so Django see the Authorization
        return req;
    })

    return axiosInstance;
};


export default useAxios;



// // Create an Axios instance with default settings
// const useAxios = axios.create({
//     baseURL: API_BASE_URL,
//     timeout: 10000000,
//     headers: {
//         "Content-Type": "application/json",
//     },
// });

// // Request interceptor for adding authentication token if available
// useAxios.interceptors.request.use(
//     async (config) => {
//         const accessToken = Cookies.get("access_token"); // Updated cookie names for consistency with your app

//         // If the access token exists, add it to the Authorization header
//         if (accessToken) {
//             config.headers.Authorization = `Bearer ${accessToken}`;
//         }

//         // If the access token is expired, attempt to refresh it
//         if (isAccessTokenExpired(accessToken)) {
//             const refreshToken = Cookies.get("refresh_token"); // Updated for consistency
//             if (refreshToken) {
//                 try {
//                     const response = await getRefreshToken(refreshToken);

//                     // Update the token cookies and headers
//                     setAuthUser(response.data.access, response.data.refresh);
//                     config.headers.Authorization = `Bearer ${response.data.access}`;
//                 } catch (error) {
//                     // Handle refresh token failure (e.g., log out user or show an error message)
//                     console.error("Token refresh failed:", error);
//                 }
//             }
//         }

//         return config;
//     },
//     (error) => Promise.reject(error)
// );

// // Response interceptor for handling errors
// useAxios.interceptors.response.use(
//     (response) => response,
//     (error) => {
//         // Handle specific error cases if needed
//         if (error.response && error.response.status === 401) {
//             // Handle unauthorized errors (e.g., redirect to login)
//             console.error("Unauthorized access - you may need to log in:", error);
//         }

//         return Promise.reject(error);
//     }
// );

// export default useAxios;






