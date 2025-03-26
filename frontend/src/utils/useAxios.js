
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






