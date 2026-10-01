<div align="center">

# 🎥 Context-Specific Video Anomaly Detection

### AI-Powered Real-Time Surveillance using Vision Transformers & Environment-Specialized Autoencoders

![Python](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge)
![PyTorch](https://img.shields.io/badge/PyTorch-DeepLearning-red?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green?style=for-the-badge)
![React](https://img.shields.io/badge/React-Frontend-61DAFB?style=for-the-badge)
![OpenCV](https://img.shields.io/badge/OpenCV-ComputerVision-orange?style=for-the-badge)

*A Context-Aware Unsupervised AI System for Real-Time CCTV Anomaly Detection*

</div>

---

# 🚀 Overview

Modern cities are equipped with thousands of surveillance cameras, making continuous human monitoring almost impossible.

Most existing anomaly detection systems rely on **supervised learning**, meaning they can only detect abnormal activities they were trained on.

This project introduces a **Context-Specific Video Anomaly Detection System** that learns **normal behaviour** instead of memorizing anomaly classes.

Unlike traditional approaches that use a single model for every environment, this system trains **multiple environment-specialized autoencoders**, enabling accurate anomaly detection across different surveillance scenarios.

Supported environments include:

- 🛣️ Street
- 🏢 Office
- 🛤️ Highway

The system performs **real-time video analysis**, detects unseen anomalies, generates alerts, and provides live analytics through an interactive dashboard.

---

# 🖥️ Project Showcase

<!-- =========================================================== -->
<!--              Paste Dashboard Screenshot Here               -->
<!-- =========================================================== -->
<img width="1920" height="1200" alt="Screenshot 2026-04-05 114130" src="https://github.com/user-attachments/assets/2909fe76-14cf-403c-9d57-0b563bf965f6" />


<br><br>

<!-- =========================================================== -->
<!--           Paste Real-Time Analytics Screenshot Here         -->
<!-- =========================================================== -->
<img width="1920" height="1200" alt="Screenshot 2026-04-05 113941" src="https://github.com/user-attachments/assets/bc5702e6-f18a-48f0-9bd6-77316c31d1e2" />


---

# ✨ Features

## 🧠 AI Features

- Context-Specific Autoencoders
- Vision Transformer (ViT) Feature Extraction
- Motion Intensity Augmentation
- Unsupervised Anomaly Detection
- Reconstruction Error Based Detection
- Detection of Previously Unseen Anomalies

---

## 🎥 Surveillance Features

- Upload CCTV Videos
- Context Selection
- Real-Time Video Analysis
- Persistent Anomaly Verification
- Automatic Alert Generation
- Live Video Preview

---

## 📊 Analytics Dashboard

- Live Anomaly Score Graph
- Detection Timeline
- Detection Log
- Alert Counter
- Normal Activity Statistics

---

## 🌐 Full Stack Application

- Responsive React Frontend
- FastAPI Backend
- Real-Time API Communication
- Interactive Dashboard

---

# 💡 Why Context-Specific Autoencoders?

Traditional anomaly detection systems train **one model** on multiple environments.

This creates confusion because the definition of **normal behaviour changes from one environment to another.**

For example,

✅ A car driving on a highway is perfectly normal.

❌ The same car driving inside an office building is clearly abnormal.

Similarly,

✅ A crowd inside a shopping mall is expected.

❌ A crowd suddenly gathering in the middle of a highway can indicate an emergency.

Instead of forcing a single model to learn every environment, this project trains **dedicated autoencoders** for each context, significantly reducing false positives while improving anomaly detection accuracy.

---

# ⚙️ Detection Pipeline

```text
Video Input
     │
     ▼
Frame Extraction
     │
     ▼
16-Frame Clip Generation
     │
     ▼
Vision Transformer (ViT)
     │
     ▼
Motion Intensity Calculation
     │
     ▼
Context Selection
(Street / Office / Highway)
     │
     ▼
Context-Specific Autoencoder
     │
     ▼
Reconstruction Error
     │
     ▼
Normal / Anomaly Classification
     │
     ▼
Persistent Verification
     │
     ▼
Real-Time Alert
```

---

# 📊 Performance

| Environment | AUC Score |
|--------------|-----------|
| 🛣️ Street | **0.856** |
| 🏢 Office | **0.908** |
| 🛤️ Highway | **0.942** |
| ⭐ Overall | **0.902** |

### Dataset

- UBnormal Dataset

---

# 🛠️ Tech Stack

### Artificial Intelligence

- Vision Transformer (ViT)
- Autoencoders
- PyTorch

### Computer Vision

- OpenCV
- Pillow

### Backend

- FastAPI
- Python

### Frontend

- React.js
- JavaScript
- HTML
- CSS

### Libraries

- NumPy
- timm

---

# ⚡ Installation

## Clone Repository

```bash
git clone https://github.com/your-username/context-specific-video-anomaly-detection.git

cd context-specific-video-anomaly-detection
```

---

## Backend

```bash
cd backend

pip install -r requirements.txt

uvicorn main:app --reload
```

Backend will start at

```
http://127.0.0.1:8000
```

---

## Frontend

```bash
cd frontend

npm install

npm run dev
```

Frontend will start at

```
http://localhost:5173
```

---

# 📈 Dashboard Features

✔️ Upload surveillance videos

✔️ Choose surveillance environment

✔️ Analyze uploaded videos

✔️ Live anomaly visualization

✔️ Interactive detection log

✔️ Automatic alert generation

✔️ Real-Time anomaly graph

✔️ Video preview

---

# 🔬 Research Contribution

This project is based on the research work:

> **Context-Specific Video Anomaly Detection using Environment-Specialized Autoencoders**

### Proposed Contributions

- Context-Specific Autoencoders
- Vision Transformer based Feature Extraction
- Motion Intensity Augmentation
- Environment-Aware Unsupervised Learning
- Real-Time Surveillance Pipeline

---

# 🚀 Future Improvements

- Automatic Context Classification
- GPU Accelerated Inference
- Multi-Camera Surveillance
- Edge AI Deployment
- Cloud Dashboard
- Mobile Notification System

---

# 👨‍💻 Author

### Dara Upendra vasu

Department of Information Technology

Gokaraju Rangaraju Institute of Engineering and Technology

Hyderabad, India

---

<div align="center">

### ⭐ If you found this project useful, consider giving it a Star!

</div>
