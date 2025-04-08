import { useState, useEffect } from 'react'
import BaseHeader from '../partials/BaseHeader'
import BaseFooter from '../partials/BaseFooter'

import apiInstance from '../../utils/axios'
import { useNavigate, useSearchParams } from 'react-router-dom';
import Toast from '../plugin/Toast';




function CreateNewPassword() {
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const navigate = useNavigate();
  const [searchParam] = useSearchParams();

  // We are able to pull out the otp and the UUIDB64 from the url in this method
  const otp = searchParam.get("otp");
  const uuidb64 = searchParam.get("uuidb64");
  const refresh_token = searchParam.get("refresh_token");


  // console.log(otp)

  const handleCreatePassword = async (event) => {
    event.preventDefault()
    setIsLoading(true)

    if (confirmPassword !== password) {
      // alert("Passwords do not match")
      Toast().fire({
        title: "Passwords do no match",
        icon: "warning"
      })
      return;
    }
    else {
      // We are creating a new form to pass our variables through
      const formdata = new FormData()
      formdata.append("password", password)
      formdata.append("otp", otp)     // we are appending or adding to the formdata so we can send this with the axios post 
      formdata.append("uuidb64", uuidb64)
      formdata.append("refresh_token", refresh_token)


      try {
        // Sending the actual post request to the backend route with our formdata. 
        await apiInstance.post(`user/password-change/`, formdata).then((res) => {
          console.log(res.data)
          setIsLoading(false)
          navigate("/login/")
          // alert(res.data.message)
          Toast().fire({
            title: res.data.message,
            icon: "warning"
          })
        });

      } catch (error) {
        console.log(error)
        setIsLoading(false)
      }
    }

    console.log("Password Created")
  }


  return (
    <>
      <BaseHeader />

      <section className="container d-flex flex-column vh-100" style={{ marginTop: "150px" }}>
        <div className="row align-items-center justify-content-center g-0 h-lg-100 py-8">
          <div className="col-lg-5 col-md-8 py-8 py-xl-0">
            <div className="card shadow">
              <div className="card-body p-6">
                <div className="mb-4">
                  <h1 className="mb-1 fw-bold">Create New Password</h1>
                  <span>
                    Choose a new password for your account
                  </span>
                </div>
                <form
                  className="needs-validation"
                  noValidate=""
                  onSubmit={handleCreatePassword}
                >
                  <div className="mb-3">
                    <label htmlFor="password" className="form-label">
                      Enter New Password
                    </label>
                    <input
                      type="password"
                      id="password"
                      className="form-control"
                      name="password"
                      placeholder="**************"
                      required=""
                      onChange={(event) => setPassword(event.target.value)}
                    />
                    <div className="invalid-feedback">
                      Please enter valid password.
                    </div>
                  </div>


                  <div className="mb-3">
                    <label htmlFor="password" className="form-label">
                      Confirm New Password
                    </label>
                    <input
                      type="password"
                      id="password"
                      className="form-control"
                      name="password"
                      placeholder="**************"
                      required=""
                      onChange={(event) => setConfirmPassword(event.target.value)}
                    />
                    <div className="invalid-feedback">
                      Please enter valid password.
                    </div>
                  </div>



                  <div>
                    <div className="d-grid">
                      {/* <button type="submit" className="btn btn-primary">
                        Save New Password <i className='fas fa-check-circle'></i>
                      </button> */}

                      {isLoading ?
                        <button disabled className="btn btn-primary">
                          Processing <i className='fas fa-spinner fa-spin'></i>
                        </button>
                        :
                        <button type="submit" className="btn btn-primary">
                          Save New Password <i className='fas fa-check-circle'></i>
                        </button>
                      }
                    </div>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      </section>

      <BaseFooter />
    </>
  )
}

export default CreateNewPassword