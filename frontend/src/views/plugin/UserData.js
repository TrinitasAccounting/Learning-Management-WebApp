
import Cookie from 'js-cookie'
import jwtDecode from 'jwt-decode'

function UserData() {
    let access_token = Cookie.get("access_token")
    let refresh_token = Cookie.get("refresh_token")

    if (access_token && refresh_token) {
        const token = refresh_token
        const decoded = jwtDecode(token)

        // We can manually decode this inside of here and get the user_id this way
        // const user_id = decoded.user_id
        // console.log(user_id)

        // Instead, simply returning the full decoded user data. It allows us to get whatever parameter we would like
        // For example: UserData().user_id  will give us the user_id of the decoded data
        return decoded
    }
    else {
        // pass
    }

}

export default UserData;





