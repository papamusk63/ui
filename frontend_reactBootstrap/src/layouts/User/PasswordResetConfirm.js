import React, { useState } from "react";
import { passwordConfirmReset } from 'api/Api'
import { useHistory } from "react-router-dom";

const PasswordResetConfirm = () => {
  let history = useHistory();
  const [password1, setPassword1] = useState('')
  const [password2, setPassword2] = useState('')
  const [error, setError] = useState(-1)
  const [isLoading, setIsLoading] = useState(false)
  const [message, setMessage] = useState('')

  const [pathname] = useState(history.location.pathname)

  const handlePassword1Change = (e) => {
    setPassword1(e.target.value)
  }
  
  const handlePassword2Change = (e) => {
    setPassword2(e.target.value)
  }
  
  const delay = ms => new Promise(res => setTimeout(res, ms));

  const handlePasswordResetConfirm = async () => {
    if (!password1.length || !password2.length) {
      setError(1)
      setMessage('password is empty')
      return
    }

    if (!password1.length || !password2.length) { 
        setError(1)
        setMessage('password did not match')
        return    
    }

    setIsLoading(true)
    const res = await passwordConfirmReset(password1, password2, pathname)
    setIsLoading(false)
    setError(0)
    if (res.success) {
      setMessage(`success: ${res.content}`)  
      await delay(3000);
      history.push('/login')
    } else {
      setMessage(`error: ${res.content}`)  
    }
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
          <label>New Password</label>
          <input
            type="password"
            className="form-control hunter-form-control"
            placeholder="Enter new password"
            value={password1}
            onChange={(e) => { handlePassword1Change(e)}}
          />
        </div>
        <div className="form-group">
          <label>Confirm Password</label>
          <input
            type="password"
            className="form-control hunter-form-control"
            placeholder="Enter confirm password"
            value={password2}
            onChange={(e) => { handlePassword2Change(e)}}
          />
        </div>
        <button
          className="btn btn-dark btn-lg btn-block hunter-signin-button"
          onClick={handlePasswordResetConfirm}
        >
          {isLoading && (
              <span className="spinner-border spinner-border-sm hunter-spinner-button" role="status" aria-hidden="true"></span>
          )}
          Reset
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

export default PasswordResetConfirm