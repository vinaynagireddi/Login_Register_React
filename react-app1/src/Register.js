import React, { useState } from "react";
import axios from 'axios';

function Register() {
    const [message, setMessage] = useState('');

    const [data,setData]=useState({
        userName:'',
        email:'',
        phNumber:'',
        password:'',
    })
    const onhandleinput = (e)=>{
        setData({
            ...data,[e.target.id]:e.target.value
        });
    };
    const handleSubmit= async ()=>{
        try{
            const res = await axios.post('http://localhost:8000/register/', data);
            setMessage(res.data.message || "Registered successfully!");
        }
        catch(error){
            setMessage("Registration failed");

            console.error(error);
        }
        setData({
      userName: '',
      phNumber: '',
      email: '',
      password: ''
    });
    }

    return(
        <div>
            <h2>Register</h2>
            <label htmlFor="userName" >User Name</label>
            <input type="text" id="userName" value={data.userName} onChange={onhandleinput}></input><br/>
            <label htmlFor="email">Email</label>
            <input type="text" id="email" value={data.email} onChange={onhandleinput}></input><br/>
            <label htmlFor="phNumber">PH Number</label>
            <input type="number" id="phNumber" value={data.phNumber} onChange={onhandleinput}></input><br/>
            <label htmlFor="password">password</label>
            <input type="password" id="password" value={data.password} onChange={onhandleinput}></input><br/>
            <button id="submit" onClick={handleSubmit}>submit</button>    
            {message && <p >{message}</p>}
  
        </div>
    );
}
export default Register;