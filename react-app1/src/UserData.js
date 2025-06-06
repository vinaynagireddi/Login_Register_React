import React, { useEffect, useState } from "react";
import axios from "axios";

function Userdata() {
  const [users, setUsers] =  useState([]);

  useEffect(() => {
    axios.get("http://localhost:8000/userdata/")
      .then((res) => {
        setUsers(res.data);
      })
      .catch((err) => {
        console.error("Error fetching user data", err);
      });
    }, []);

  return (
    <div>
      <h2>All Users</h2>
      <table border="1">
        <thead>
          <tr>
            <th>User Name</th>
            <th>Email</th>
            <th>Phone Number</th>
          </tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr>
              <td>{u.userName}</td>
              <td>{u.email}</td>
              <td>{u.phNumber}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <button onClick={() => window.open("http://localhost:8000/download-users/")}>Download</button>
    </div>
  );
};

export default Userdata;
