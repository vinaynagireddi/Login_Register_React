import React, { useEffect, useState } from "react";
import axios from "axios";
import './UserData.css';

function Userdata() {
  const [users, setUsers] = useState([]);
  const [editedUsers, setEditedUsers] = useState([]);
  const sessionKey = localStorage.getItem("sessionKey");

  useEffect(() => {
    axios.get("http://localhost:8000/userdata/", {
      headers: {
        "X-Session-Key": sessionKey
      }
    })
    .then((res) => {
      if (Array.isArray(res.data)) {
        setUsers(res.data);
        setEditedUsers(res.data);
      } else {
        alert(res.data.message || "Unexpected response format");
      }
    })
    .catch((err) => {
      if (err.response?.status === 401) {
        alert("Session expired. Please login again.");
        window.location.href = "/login";
      } else {
        console.error("Error fetching user data", err);
        alert("Failed to fetch user data.");
      }
    });
  }, []);

  const handleChange = (index, field, value) => {
    const updated = [...editedUsers];
    updated[index][field] = value;
    setEditedUsers(updated);
  };

  const handleSave = () => {
    axios.post("http://localhost:8000/userdata/", editedUsers, {
      headers: {
        "X-Session-Key": sessionKey
      }
    })
    .then((res) => {
      alert(res.data.message || "User data updated successfully!");
    })
    .catch((err) => {
      if (err.response?.status === 403) {
        alert("You are not authorized to make changes.");
      } else if (err.response?.status === 401) {
        alert("Session expired. Please login again.");
        window.location.href = "/login";
      } else {
        console.error("Error saving user data", err);
        alert("Failed to save user data.");
      }
    });
  };

  const handleLogout = () => {

  axios.post("http://localhost:8000/logout/", null, {
    headers: {
      "X-Session-Key": sessionKey
    },
  })
  .then((res) => {
    alert(res.data.message || "Logged out successfully!");
    localStorage.removeItem("sessionKey");
    window.location.href = "/login";
  })
  .catch((err) => {
    console.error("Logout failed:", err);
    alert("Logout failed. Try again.");
  });
};


  return (
    <div className="users-container">
      <h2>All Users</h2>
      <table className="users-table" border="1">
        <thead>
          <tr>
            <th>User Name</th>
            <th>Email</th>
            <th>Phone Number</th>
            <th>Role</th>
          </tr>
        </thead>
        <tbody>
          {editedUsers.map((u, index) => (
            <tr key={index}>
              <td>
                <input
                  type="text"
                  value={u.userName}
                  onChange={(e) => handleChange(index, 'userName', e.target.value)}
                />
              </td>
              <td>{u.email}</td>
              <td>
                <input
                  type="text"
                  value={u.phNumber}
                  onChange={(e) => handleChange(index, 'phNumber', e.target.value)}
                />
              </td>
              <td>{u.role}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <button className="save-btn" onClick={handleSave}>Save Changes</button>
      <button
        className="download-btn"
        onClick={() => window.open("http://localhost:8000/download-users/")}
      >
        Download
      </button>
      <button className="logout" onClick={handleLogout}>Logout</button>
    </div>
  );
}

export default Userdata;
