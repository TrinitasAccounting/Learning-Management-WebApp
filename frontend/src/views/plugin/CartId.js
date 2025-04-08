

// Getting the cart id from the local storage or creating a new random string for the cart
function CartId() {
    // creating a random string that can be used for the cartId if doesn't already have one
    const generateRandomString = () => {
        const length = 8;
        const characters = '1234567890';
        let randomString = "";

        for (let i = 0; i < length; i++) {
            const randomIndex = Math.floor(Math.random() * characters.length)

            randomString += characters.charAt(randomIndex)
        }

        // Setting the local storage item (or creating it) called randomString to be the random character string we created above
        localStorage.setItem('randomString', randomString)
    }

    // Getting the random string if it is in storage
    const existingRandomString = localStorage.getItem("randomString")

    if (!existingRandomString) {
        generateRandomString()
    }
    else {

    }

    return existingRandomString
}

export default CartId












