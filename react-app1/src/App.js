import './App.css';
import React from 'react';
import Register from './Register';
import Login from './login';
import {Routes,Route,Link} from 'react-router-dom';
import UserData from './UserData';

function Home() {
  return (
    <div className='App'>
      <h1>Welcome</h1>
      <Link to="/register"><button>Register</button></Link>
      <Link to="/login"><button>Login</button></Link>
    </div>
  );
}
function App() {
  return (
    <Routes>
      <Route path='/' element={<Home />} />
      <Route path='/register' element={<Register />} />
      <Route path='/login' element={<Login />} />
      <Route path='/userdata' element={<UserData />} />
    </Routes>
  );
}

export default App;
