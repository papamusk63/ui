import React, { useState } from "react";
import { validateEmail } from 'utils/helper'
import { forgotPassword } from 'api/Api'

const ForgotPassword = () => {
  const [email, setEmail] = useState('')
  const [error, setError] = useState(-1)
  const [isLoading, setIsLoading] = useState(false)
  const [message, setMessage] = useState('')
    
  const handleEmailChange = (e) => {
    setEmail(e.target.value)
  }
    
  const handleForgotPassword = async () => {
    if (!validateEmail(email)) {
      setError(1)
      setMessage('Invalid Email!')
      return
    }
    setIsLoading(true)
    let result = await forgotPassword(email)
    setIsLoading(false)
    if ( result.success ) {
      setError(0)
      setMessage('Password is sent to your email')
      return
    }
    setError(1)
    setMessage('Invalid Email!')
    return
  }

  const handleModalClose = () => {
    setError(-1);
    setMessage('');
  }

  return (
    <div className={"login-form"}>
      <div>
        <h3 className="hunter-mb-3">Forgot Password</h3>

        <div className="form-group">
          <label>Email</label>
          <input
            type="text"
            className="form-control hunter-form-control"
            placeholder="Enter email"
            value={email}
            onChange={(e) => { handleEmailChange(e)}}
          />
        </div>
          <button
            className="btn btn-dark btn-lg btn-block hunter-signin-button"
            onClick={handleForgotPassword}
          >
            {isLoading && (
                <span className="spinner-border spinner-border-sm hunter-spinner-button" role="status" aria-hidden="true"></span>
            )}
            Send
          </button>
          <div className="form-group">
            <p className="sign-up-area text-right">
                <a href="/signin">Sign In?</a>
            </p>
          </div>
      </div>
      {error !== -1 && 
        <div class="alert alert-primary" role="alert">
          <div className="alert-container">
            <div className="alert-content">
              {message}
            </div>
            <button type="button" className="btn btn-primary modal-close-button hunter-modal-small-button" onClick={() => { handleModalClose() }}>Close</button>
          </div>
        </div>   
      }
    </div>
  );
}

export default ForgotPassword