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

    const inputHandle=(e)=>{
        setData({...data,[e.target.id]:e.target.value})
    }
    const handleSubmit= async ()=>{
        try{
            const res = await axios.post('http://localhost:8000/login/', data);
            if (res.data.message === "Login Successfully") {
            navigate('/userdata'); 
            }

        }catch(error){
            console.error(error);
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
            <button id="submit" onClick={handleSubmit}>submit</button>
        </div>
    )
};

export default Login;