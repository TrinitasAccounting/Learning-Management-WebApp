
import { Navigate } from 'react-router-dom'
import { useAuthStore } from '../store/auth';


// this is going to check if a user is logged in. We will wrap our protected routes with this wrapper, and only if there is a user logged in will it show the children
const PrivateRoute = ({ children }) => {
    const loggedIn = useAuthStore((state) => state.isLoggedIn)();         // we are calling the isLoggedIn function from the store. 

    return loggedIn ? <>{children}</> : <Navigate to="/login/" />;

};


export default PrivateRoute;







