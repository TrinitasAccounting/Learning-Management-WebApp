
import { useEffect, useState } from 'react';
import { setUser } from '../utils/auth';


// We will wrap our entire application in this code, and as soon as our application gets mounted. This code will get called and ran
const MainWrapper = ({ children }) => {
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const handler = async () => {
            setLoading(true)

            await setUser();

            setLoading(false);
        }

        // Calling the function that we just created
        handler();
    }, [])

    // Since it wraps our entire application. Children will refer to all other components below this wrapper. If loading (or basically no User) then it will render null until a User is set and then it will allow all children below it to render on the screen
    return (
        <>
            {loading ? null : children}
        </>
    )

};


export default MainWrapper;








