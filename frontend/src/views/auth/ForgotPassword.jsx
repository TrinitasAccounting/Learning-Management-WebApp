import React from 'react'
import { useState, useEffect } from 'react'

import BaseHeader from '../partials/BaseHeader'
import BaseFooter from '../partials/BaseFooter'
import { Link } from 'react-router-dom'

import apiInstance from '../../utils/axios';
import Toast from '../plugin/Toast'




function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);


  const handleEmailSubmit = async (event) => {
    event.preventDefault();
    setIsLoading(true)

    try {
      // This is how we are sending the get to the email password-reset backend url, and it returns a response back to us
      await apiInstance.get(`user/password-reset/${email}/`).then((res) => {
        console.log(res.data)
        setIsLoading(false)
        // alert("Password Reset Email Sent")
        Toast().fire({
          title: "Password Reset Email Sent",
          icon: "warning"
        })
      })

    } catch (error) {
      console.log("error: ", error)
      setIsLoading(false)
    }

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
                  <h1 className="mb-1 fw-bold">Forgot Password</h1>
                  <span>
                    Let's help you get back into your account
                  </span>
                </div>
                <form
                  className="needs-validation"
                  noValidate=""
                  onSubmit={handleEmailSubmit}
                >
                  <div className="mb-3">
                    <label htmlFor="email" className="form-label">Email Address</label>
                    <input
                      type="email"
                      id="email"
                      className="form-control"
                      name="email"
                      placeholder="johndoe@gmail.com"
                      required
                      onChange={(event) => setEmail(event.target.value)}
                    />
                  </div>

                  <div>
                    <div className="d-grid">
                      {/* <button type="submit" className="btn btn-primary">
                        Reset Password <i className='fas fa-arrow-right'></i>
                      </button> */}
                      {isLoading ?
                        <button disabled className="btn btn-primary">
                          Processing <i className='fas fa-spinner fa-spin'></i>
                        </button>
                        :
                        <button type="submit" className="btn btn-primary">
                          Reset Password <i className='fas fa-arrow-right'></i>
                        </button>}
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

export default ForgotPassword