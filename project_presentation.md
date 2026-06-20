# CycloneOPS PRO - Project Presentation

---

## Slide 1: Title

# CycloneOPS PRO 🌀

**Project Title:** CycloneOPS PRO - Cyclone Intensity Prediction System

**Batch Members:**
- Member 1 – Register No.
- Member 2 – Register No.
- Member 3 – Register No.

**Guide Name:** [Guide Name]
**Department:** [Department Name]

---

## Slide 2: Introduction

### Domain Overview
Cyclone prediction uses meteorological data to estimate storm intensity and track. Accurate forecasting helps protect lives and infrastructure. This project combines machine learning with a web dashboard. It focuses on cyclone classification using Indian Meteorological Department categories. The system supports both real-time and batch predictions.

### Motivation
- Enable faster cyclone intensity forecasts.
- Improve decision support for disaster management.
- Reduce reliance on manual weather analysis.
- Provide a simple web interface for non-technical users.

---

## Slide 3: Objective

### Primary Goals
- Build a machine learning model for cyclone intensity classification.
- Deliver a user-friendly web application for predictions.
- Support batch CSV uploads and model retraining.
- Provide secure API access and data visualization.

### Problem Statement
The project aims to solve inaccurate cyclone intensity prediction from existing systems by applying a neural network model and a web-based dashboard. It addresses the need for rapid, automated classification of cyclone strength using meteorological inputs.

---

## Slide 4: Existing System

### Current Methods
- Meteorologists rely on manual analysis and rules-based forecasting.
- Traditional models use statistical regression or physical simulation.
- Many systems lack easy user interfaces or API access.
- Existing tools do not support batch prediction or retraining.

### Domain Status
Cyclone forecasting today is often siloed in weather centers. Analysts use separate tools for data cleaning, prediction, and reporting. There is a gap in providing integrated machine learning with interactive visualization.

---

## Slide 5: Limitations of Existing System

### Drawbacks
- Limited automation and high manual effort.
- Poor support for batch data processing.
- Inflexible models that cannot retrain with new data.
- Outputs are not always accessible through web dashboards.

### Need for New Approach
A new system is needed to combine ML prediction with a modern web interface. This approach improves usability, scalability, and accuracy for cyclone intensity forecasting.

---

## Slide 6: Proposed System

### New Features
- PyTorch-based cyclone intensity classification model.
- Flask REST API for prediction and retraining.
- Web dashboard with interactive map visualizations.
- CSV upload support for batch inference.
- Secure user login and session management.

### How It Improves Existing Systems
- Automates prediction using a trained neural network.
- Simplifies interaction with a browser-based dashboard.
- Allows model updates with new cyclone data.
- Presents a unified solution for weather analysts.

---

## Slide 7: Software Requirements Specification (SRS)

### Hardware Requirements
- Processor: Intel Core i5 or equivalent
- RAM: 8 GB minimum
- Storage: 5 GB free disk space
- Network: Internet access for APIs and dashboards

### Software Requirements
- OS: Windows 10/11, Linux, or macOS
- Languages: Python 3.11+
- Frameworks: Flask, PyTorch
- Tools: Docker, Git
- Libraries: Pandas, NumPy, Joblib, Flask-Login, Flask-CORS

---

## Slide 8: System Architecture / System Design

### Architecture Overview
- Frontend: HTML/CSS/JavaScript dashboard with map visualization.
- Backend: Flask API server handles prediction, training, and data.
- ML Core: PyTorch model, preprocessing scaler, label encoder.
- Data Layer: CSV dataset, cleaned training data, saved model files.

### Workflow
1. User logs into the web dashboard.
2. User submits cyclone input or CSV file.
3. Backend preprocesses data and calls the ML model.
4. Prediction results are returned and displayed.
5. Optionally, new data can retrain the model.

---

## Slide 9: Module Description (System Design part 2)

### Project Modules
- User Interface Module
- API Module
- Prediction Module
- Training Module
- Data Processing Module

### Module Diagrams
- Data Flow: Input → Preprocessing → Model → Output
- Use Case: User login, make prediction, upload CSV, retrain model
- System Components: Frontend, Backend, ML Core, Data Storage

---

## Slide 10: System Implementation - Environment & Data

### Tools and Technologies
- Python 3.11
- Flask web framework
- PyTorch for model building
- Docker for containerization
- Leaflet.js for map visualization
- Pandas and NumPy for data handling

### Dataset Description
- Source: Project dataset in `data/raw/New_Data.csv`
- Size: 8 cyclone records in raw data
- Features: Wind speed, pressure, temperature, humidity, latitude, longitude, timestamp, category labels
- Processed data stored in `data/processed/clean_data.csv`

---

## Slide 11: System Implementation - Algorithm & Methodology

### Core Algorithm
- Feedforward neural network implemented in PyTorch.
- Input features normalized with a scaler.
- Output predicts cyclone intensity categories.
- Cross-entropy loss and Adam optimizer for training.

### Methodology Steps
1. Load raw cyclone data from CSV.
2. Clean, validate, and preprocess features.
3. Encode target categories.
4. Train the PyTorch model on processed data.
5. Save model, scaler, and label encoder for inference.
6. Use Flask API for prediction and retraining workflows.

---

## Slide 12: Testing and Evaluation Metrics

### Testing Types
- Unit testing of data preprocessing functions.
- API testing for prediction and upload endpoints.
- Functional testing of the web dashboard.
- Model evaluation on training/validation splits.

### Evaluation Metrics
- Accuracy
- Loss
- Precision / Recall
- F1-score
- Inference latency for prediction requests

### Comparison
- Model performance vs. baseline rule-based methods
- Training accuracy vs. validation accuracy
- [Include charts or tables if available]

---

## Slide 13: Output / Screenshots

### Final Application Screenshots
- Dashboard interface with map view
- Prediction results screen
- CSV upload and batch prediction view
- Model training status or API response

### Visual Proof
- Show the system working end-to-end
- Display example cyclone prediction results
- Highlight secure login and interactive visualization

---

## Slide 14: Conclusion and Future Scope

### Conclusion
- Developed a cyclone intensity prediction system using ML and web technologies.
- Delivered a user-friendly dashboard with API integration.
- Improved automation and streamlined cyclone forecasting workflows.

### Future Scope
- Add live weather API data ingestion.
- Extend dataset for more cyclone cases.
- Use advanced sequence models like LSTM.
- Deploy to cloud with CI/CD and monitoring.

**Thank You!**

### Q&A
- Questions are welcome.
- Discussion on implementation and next steps.