import React, { useState, useEffect } from "react";
import {
    useHistory,
} from "react-router-dom";
import { useAuth } from 'contexts/authContext'
import { validateEmail } from 'utils/helper'

const Login = () => {
    let auth = useAuth();
    let history = useHistory();
    const [error, setError] = useState(-1)
    const [isLoading, setIsLoading] = useState(false)
    const [message, setMessage] = useState('')
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')

    useEffect(() => {
        const listener = event => {
            if (event.code === "Enter" || event.code === "NumpadEnter") {
                event.preventDefault();
                login();
            }
        };
        document.addEventListener("keydown", listener);
        return () => {
            document.removeEventListener("keydown", listener);
        };
    }, []);

    const handleEmailChange = (e) => {
        setEmail(e.target.value)
    }
    
    const handlePasswordChange = (e) => {
        setPassword(e.target.value)
    }
    
    const login = async () => {
        if (!email.length || !password.length) {
            setError(1)
            setMessage('Email or password is wrong')
            return
        }
        
        if (!validateEmail(email)){
            alert('Invalid email')
            return
        }
        
        setIsLoading(true)
        const res = await auth.authUser.signin(email, password)
        setIsLoading(false)
        if (res.success) {
            const historyState = {
                userId: res.user_id
            }
            history.push({
                pathname: '/verify',
                state: historyState
            })
        } else {
            setError(1)
            setMessage(res.error)
            return
        }
    }

    const handleModalClose = () => {
        setError(-1);
        setMessage('');
    }

    return (
        <div className={"login-form"}>
            <div>

                <h3>Log In</h3>

                <div className="form-group">
                    <label>User Email</label>
                    <input
                        type="email"
                        className="form-control hunter-form-control"
                        placeholder="Enter user email"
                        value={email}
                        onChange={(e) => { handleEmailChange(e)}}
                        required
                    />
                </div>

                <div className="form-group">
                    <label>Password</label>
                    <input
                        type="password"
                        className="form-control hunter-form-control"
                        placeholder="Enter password"
                        value={password}
                        onChange={(e) => { handlePasswordChange(e)}}
                        required
                    />
                </div>

                <div className="form-group">
                    <div className="custom-control custom-checkbox">
                        <input type="checkbox" className="custom-control-input" id="customCheck1" />
                        <label className="custom-control-label" htmlFor="customCheck1">Remember me</label>
                    </div>
                </div>

                <button
                    className="btn btn-dark btn-lg btn-block hunter-signin-button"
                    onClick={login}
                >
                    {isLoading && (
                        <span className="spinner-border spinner-border-sm hunter-spinner-button" role="status" aria-hidden="true"></span>
                    )}
                    Sign in
                </button>
                
                <div className="form-group hunter-form-signup-area">
                    <p className="sign-up-area text-left">
                        <a href="/signup">Sign Up?</a>
                    </p>
                    <p className="forgot-password text-right">
                        Forgot <a href="/forgot_password">password?</a>
                    </p>
                </div>
            </div>
            {error !== -1 && 
                <div className="alert alert-primary" role="alert">
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

export default Login