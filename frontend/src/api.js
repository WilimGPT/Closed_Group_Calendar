import axios from "axios"

const api = axios.create({
  baseURL: "https://closed-group-calendar.onrender.com/api/",
  headers: {
    "Content-Type": "application/json"
  }
})

export default api
