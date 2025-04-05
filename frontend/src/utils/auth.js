
import { useAuthStore } from '../store/auth';
import axios from './axios'                            // we are importing our axios.js file so we can use the apiInstance function but we are calling it "axios" in our functions because that is how we imported it as
import jwt_decode from "jwt-decode";
import Cookie from 'js-cookie';
import Swal from "sweetalert2";


// This is our function to login in a user, taking an email and a password from the user
export const login = async (email, password) => {
    try {
        // We set up the route to login in users at /api/v1/user/token/   on the backend, so we are sending a post request to this route. And in return the jwt will provide us back an access token and a refresh token IF THE USER EXIST AND CREDENTIALS PASS ON THE BACKEND
        const { data, status } = await axios.post(`user/token/`, {
            email,
            password,
        });

        if (status === 200) {
            setAuthUser(data.access, data.refresh)
            // alert("Login Successfull")
        }

        return { data, error: null };

    } catch (error) {
        const errorMessage = error.response?.data?.detail || "Something went wrong";
        console.error("Login error:", errorMessage);
        return { data: null, error: errorMessage };
    }
};



// This is our function to register as new user
// in the future, all we have to do is call this "register(___, ____, ____)" and it will register a user
export const register = async (full_name, email, password, password2) => {
    try {
        const { data } = await axios.post(`/user/register/`, {
            full_name,
            email,
            password,
            password2
        });

        await login(email, password);             // by calling this, it will automatically log the user in
        // alert("Registration Successfull")

        return { data, error: null };

    } catch (error) {
        // we are just accessing the specific error messages in this manner, and this allows us to output useful and actionable error messages on the front end
        //alert(`${error.response.data.full_name} - ${error.response.data.email} - ${error.response.data.password} - ${error.response.data.password2}`)

        return {
            data: null,
            error: `${error.response.data.full_name} - ${error.response.data.email} - ${error.response.data.password} - ${error.response.data.password2}` || "Something went wrong",
        }

    }
};



export const logout = () => {
    Cookie.remove("access_token")
    Cookie.remove("refresh_token")
    useAuthStore.getState().setUser(null)     // we can call the usAuthStore since we imported it, then call the getState() function to access the state parameters we have in there. Then we are calling setUser() to set this state and setting is to null

    // alert("You have been logged out")
};




export const setUser = async () => {
    const access_token = Cookie.get('access_token')     // this is how we can get things that are stored in the cookies
    const refresh_token = Cookie.get("refresh_token")

    if (!access_token || !refresh_token) {
        console.log("Token does not exist")
        return;
    }

    if (isAccessTokenExpired(access_token)) {
        const response = await getRefreshedToken(refresh_token);
        setAuthUser(response.data.access, response.data.refresh)
    }
    else {
        setAuthUser(access_token, refresh_token)
    }

};



export const setAuthUser = (access_token, refresh_token) => {
    if (access_token && refresh_token) {
        Cookie.set('access_token', access_token, {
            expires: 10000,                      // access_token expires after 1 day (should be a 1)
            secure: true,
        });

        Cookie.set('refresh_token', refresh_token, {
            expires: 7000,                      // access_token expires after 7 days (should be a 7)
            secure: true,
        });

        // const user = jwt_decode(access_token) ?? null           // jwt_decode will go and get the user information from the access_token that it receives or sees
        const user = access_token ? jwt_decode(access_token) : null;
        if (user) {
            useAuthStore.getState().setUser(user);               // accessing the store and using getState() in order for us to pick what state function we want to call. Then call the setUser function from our store
        }

    } else {
        console.error("invalid tokens, could not set user.")
    }

    useAuthStore.getState().setLoading(false);
};



export const getRefreshedToken = async () => {

    try {

        const refresh_token = Cookie.get("refresh_token");
        const response = await axios.post(`user/token/refresh/`, {                   // this returns us a new token when posting a refresh token to this route
            refresh: refresh_token,
        })
        return response.data;

    } catch (error) {
        console.error("Failed to refresh token:", error);
        logout(); // Log the user out if refresh fails
        throw error;
    }

};



export const isAccessTokenExpired = (access_token) => {
    try {
        const decodedToken = jwt_decode(access_token)
        return decodedToken.exp < Date.now() / 1000                      // this allows us to check if the access_token has expired
    } catch (error) {
        console.log("Error decodign token: ", error)
        return true;
    }
};






