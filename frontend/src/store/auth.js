import { create } from 'zustand'
import { mountStoreDevtool } from 'simple-zustand-devtools'


const useAuthStore = create((set, get) => ({
    allUserData: null,
    loading: false,

    // Creating a user function that will populate if there is a user and keep track of user related data
    user: () => ({
        user_id: get().allUserData?.user_id || null,      // this is essentially saying, to go get the user_id from the allUserData, and if not there then it can be null
        username: get().allUserData?.username || null
    }),

    // This is setting the user to equal the allUserData. 
    setUser: (user) => set({
        allUserData: user
    }),

    // This will allow us to set the loading state to true or false
    setLoading: (loading) => set({ loading }),

    isLoggedIn: () => get().allUserData !== null
}));




// This allows the developer to debug the store when in the development environment
if (import.meta.env.DEV) {
    mountStoreDevtool("Store", useAuthStore)
}


// Our export of the store so we can use the states and functions in our components
export { useAuthStore };







