import React, { useEffect, useState } from "react";
import axios from "axios";
import './UserData.css';

function Userdata() {
  const [users, setUsers] = useState([]);
  const [editedUsers, setEditedUsers] = useState([]);

  useEffect(() => {
    axios.get("http://localhost:8000/userdata/")
      .then((res) => {
        setUsers(res.data);
        setEditedUsers(res.data); // copy to editable state
      })
      .catch((err) => {
        console.error("Error fetching user data", err);
      });
  }, []);

  const handleChange = (index, field, value) => {
    const updated = [...editedUsers];
    updated[index][field] = value;
    setEditedUsers(updated);
  };

  const handleSave = () => {
    axios.put("http://localhost:8000/userdata/", editedUsers)
      .then(() => {
        alert("User data updated successfully!");
      })
      .catch((err) => {
        console.error("Error saving user data", err);
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
            </tr>
          ))}
        </tbody>
      </table>

      <button className="save-btn" onClick={handleSave}>Save Changes</button>
      <button className="download-btn" onClick={() => window.open("http://localhost:8000/download-users/")}>Download</button>
    </div>
  );
}

export default Userdata;
