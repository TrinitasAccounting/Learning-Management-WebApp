
import { useState, useEffect } from "react";

function GetCurrentAddress() {
    const [add, setAdd] = useState("")

    useEffect(() => {
        // Using the builtin navigator and geolocation functions to find the latitude and longitude
        navigator.geolocation.getCurrentPosition(pos => {
            const { latitude, longitude } = pos.coords;             // these names are important as this is what it is actually called in the "pos.coords"

            const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}`;

            // The url response will have a parameter called "address" in it
            fetch(url).then(res => res.json()).then(data => setAdd(data.address))
        })
    }, [])

    return add


}

export default GetCurrentAddress;







