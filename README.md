# ☀️ AI-Based Solar Energy Prediction System  


This project predicts **solar power output (AC Power)** using real-time weather and panel operating conditions.  
The model assists in **energy planning, load balancing, and storage optimization** — helping reduce reliance on fossil backup and improving renewable energy efficiency.

---

## 🔥 Project Overview

Solar power generation is **highly dependent on environmental factors** like temperature and solar irradiation.  
Fluctuations make it challenging to maintain **grid stability and storage efficiency**.

This project uses **Machine Learning** to accurately forecast **AC Power Output**, using sensor readings recorded from a **real solar PV plant in India** (Plant-1 Dataset).

---

## 📊 Dataset Details

- **Source:** Kaggle – *Solar Power Generation Data (Plant-1)*
- **Origin:** A real **grid-connected solar power plant in India**
- **Note:** The operating company is **not disclosed** for confidentiality.
- Contains:
  - **Generation Data** (AC power, DC power, yields)
  - **Weather Data** (ambient & module temperature, irradiation)
  - Multiple **inverters (SOURCE_KEY)** under **PLANT_ID**

---

## 🧠 Machine Learning Workflow

| Stage | Description |
|------|-------------|
| **Data Cleaning** | Handled missing values & removed inconsistencies |
| **Feature Engineering** | Extracted datetime factors (`hour`, `month`, `dayofyear`, `sin_hour`, `cos_hour`) |
| **Scaling** | Applied MinMaxScaler for normalized learning |
| **Model Training** | Trained multiple regression models |
| **Evaluation** | Compared real vs predicted values to choose the most accurate model |

---

## 🤖 Models Trained

| Model | Purpose | Status |
|-------|--------|--------|
| **Random Forest Regressor** | Primary prediction model | ✅ Used in App |
| **XGBoost Regressor** | Secondary performance model | ✅ Used if available |
| **LSTM Neural Network** | Time-series learning model | ✅ Trained, optional usage |

The best-performing model is used in the **Final Prediction Dashboard**.

---

## 🎯 Features Used for Prediction

| Feature | Meaning |
|--------|--------|
| `ambient_temperature` | External weather temperature |
| `module_temperature` | Solar panel temperature |
| `irradiation` | Incoming solar radiation |
| `hour` / `month` / `dayofyear` | Time-based energy variation patterns |
| `sin_hour`, `cos_hour` | Smooth daily cyclic behavior |

**Target Variable:** `ac_power`

---

## 🖥️ Web Dashboard (Flask)

A clean, modern web interface enables real-time prediction:

### **🔗 Live Local Access**

### Deployed On Vercel
https://solar-energy-project-76amy8hrl-ishani-chakravartys-projects.vercel.app/
