import './login.css';
import axios from "axios";
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
function Login () {
    const [data,setData]=useState({
        email:'',
        password:'',
    });
    const navigate = useNavigate();

    const [message, setMessage] = useState('');

    const inputHandle=(e)=>{
        setData({...data,[e.target.id]:e.target.value})
    }
    const handleSubmit= async ()=>{
        try{
            const res = await axios.post('http://localhost:8000/login/', data);
            setMessage(res.data.message);
            if ( res.status === 200) {
                localStorage.setItem("sessionKey", res.data.sessionKey);
            navigate('/userdata'); 
            }

        }catch(error){
            setMessage(error.response?.data?.message || "Login failed. Please try again.");
        }
        setData({
            email:'',
            password:''
        })
    };
    

    return(
        <div className='login-box'>
            <h1>Login</h1>
            <label htmlFor="email">Email</label>
            <input id="email" type="text" value={data.email} onChange={inputHandle}></input><br/>
            <label htmlFor="password">password</label>
            <input id="password" type="password" value={data.password} onChange={inputHandle}></input><br/>
            <button id="submit" onClick={handleSubmit}>Login</button>
            {message && <p >{message}</p>}
        </div>
    )
};

export default Login;