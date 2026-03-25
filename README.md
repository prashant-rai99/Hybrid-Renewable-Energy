# ⚡ Hybrid Renewable Energy Management System

An advanced **AI-powered Hybrid Renewable Energy Management System** designed to intelligently monitor, predict, and optimize energy generation from multiple renewable sources such as **solar and wind**.

This project aims to solve real-world energy challenges by combining **machine learning, real-time analytics, and an interactive dashboard** to ensure efficient energy utilization and sustainability.

---

## 🌍 Problem Statement

Traditional energy systems lack:

* Real-time monitoring of renewable sources
* Accurate prediction of energy generation
* Efficient optimization of available resources
* Insights into environmental impact

This leads to **energy wastage, inefficiency, and poor decision-making**.

---

## 💡 Solution

This system provides an integrated platform that:

* Monitors energy data in real time
* Uses AI models to forecast energy production
* Suggests optimized usage strategies
* Visualizes insights through a modern dashboard

---

## 🚀 Key Features

### 🔋 Real-Time Monitoring

* Track energy generation from solar and wind sources
* Visualize live system performance

### 📊 AI-Based Forecasting

* Predict energy generation using trained ML models
* Supports multiple locations and datasets

### ⚙️ Energy Optimization

* Intelligent recommendations for efficient power usage
* Helps reduce energy wastage

### 🌱 Carbon Analytics

* Analyze environmental impact
* Estimate carbon footprint and sustainability metrics

### 📈 Interactive Dashboard

* Clean and modern UI
* Easy navigation across modules
* Responsive design for all devices

---

## 🧠 Tech Stack

### 🔹 Frontend

* Next.js
* React
* Tailwind CSS
* Component-based UI architecture

### 🔹 Backend

* FastAPI
* Python

### 🔹 Machine Learning

* Trained models for:

  * Solar energy prediction
  * Wind energy prediction

---

## 🏗️ System Architecture

The system is divided into three main layers:

1. **Frontend (User Interface)**

   * Displays dashboards and analytics
   * Sends requests to backend

2. **Backend (API Layer)**

   * Handles logic and API endpoints
   * Processes user inputs
   * Communicates with ML models

3. **ML Models Layer**

   * Predict energy generation
   * Provide data for optimization

---

## 📂 Project Structure

```
Hybrid-Renewable-Energy/
│
├── app/                        # Frontend (Next.js)
│   ├── dashboard/
│   ├── login/
│   ├── signup/
│   └── ...
│
├── backend/                   # Backend (FastAPI)
│   ├── main.py
│   ├── energy_optimizer.py
│   └── models/                # ML models (excluded from repo)
│
├── components/                # Reusable UI components
├── public/                    # Static assets
├── styles/                    # CSS files
├── package.json
└── README.md
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```
git clone https://github.com/prashant-rai99/Hybrid-Renewable-Energy
cd Hybrid-Renewable-Energy
```

---

### 2️⃣ Install Frontend Dependencies

```
npm install
```

---

## ▶️ Running the Project

### 🔹 Start Frontend

```
npm run dev
```

Frontend will run at:
👉 http://localhost:3000

---

### 🔹 Start Backend

```
cd backend
uvicorn main:app --reload
```

Backend will run at:
👉 http://127.0.0.1:8000

---

## ⚠️ Important Note (Models)

Due to GitHub file size limitations, ML model files (`.pkl`) are not included in the repository.

You must place the models manually inside:

```
backend/models/
```

---

## 📊 How It Works

1. User interacts with dashboard
2. Frontend sends request to backend
3. Backend processes request and calls ML model
4. Model returns prediction
5. Data is displayed visually on dashboard

---

## 🔥 Use Cases

* Smart energy grid management
* Renewable energy plants
* College/research projects
* Sustainability tracking systems
* AI-based optimization systems

---

## 🚀 Future Enhancements

* 🔐 User authentication system
* 🌐 Live weather API integration
* 📡 IoT-based real-time sensor data
* 📊 Advanced deep learning models
* ☁️ Cloud deployment (AWS / Azure)
* 📱 Mobile application

---

## 🤝 Contributing

Contributions are welcome!

Steps:

1. Fork the repository
2. Create a new branch
3. Make changes
4. Commit and push
5. Create a Pull Request

---

## 👨‍💻 Author

**Prashant Rai**
B.Tech CSE (AI)
KIET Group of Institutions

---

## ⭐ Why This Project Matters

This project demonstrates:

* Real-world problem solving
* Integration of AI with web systems
* Full-stack development skills
* Understanding of renewable energy systems

It reflects the ability to build **scalable, intelligent, and impactful solutions**.

---

## 📌 Conclusion

The Hybrid Renewable Energy Management System is a step toward **smart and sustainable energy solutions**, combining **AI, data analytics, and modern web technologies** into one powerful platform.

---

⚡ *Building smarter energy systems for a sustainable future.*
