# Churn Prediction API Documentation

## Overview
This API provides telecom companies with tools to predict customer churn, analyze customer data, and generate actionable insights to reduce customer attrition.

## Authentication
All endpoints require authentication via JWT token. Include the token in the Authorization header:
```
Authorization: Bearer <your_token>
```

## API Endpoints

### 1. Single Customer Prediction
**Endpoint:** `POST /predict`
**Description:** Predict churn for a single customer with reasons and recommendations

**Request Body:**
```json
{
  "customer_id": "cust_12345",
  "tenure": 12,
  "monthly_charges": 75.50,
  "total_charges": 906.00,
  "contract_type": "Month-to-month",
  "internet_service": "Fiber optic",
  "payment_method": "Electronic check"
}
```

**Response:**
```json
{
  "customer_id": "cust_12345",
  "churn_probability": 0.75,
  "churn_label": "Yes",
  "churn_reason": "High monthly charges",
  "recommendations": [
    "Offer discount or promotional pricing",
    "Review current plan and suggest cost optimization"
  ]
}
```

### 2. Batch CSV Upload
**Endpoint:** `POST /upload`
**Description:** Upload CSV file with multiple customers and get predictions with overview data

**Request:** 
- Content-Type: `multipart/form-data`
- File: CSV file with customer data

**Required CSV Columns:**
```
gender, SeniorCitizen, Partner, Dependents, tenure, PhoneService, MultipleLines,
OnlineSecurity, OnlineBackup, DeviceProtection, TechSupport, StreamingTV, 
StreamingMovies, PaperlessBilling, MonthlyCharges, TotalCharges
```

**Response:**
```json
{
  "total_records": 100,
  "results": [
    {
      "customer_id": "cust_1",
      "churn_probability": 0.85,
      "churn_label": "Yes",
      "churn_reason": "Short customer tenure (less than 1 year)",
      "recommendations": ["Offer onboarding support", "Provide early-bird incentives"]
    }
  ],
  "overview": {
    "total_customers": 100,
    "churn_risk": {
      "high": 30,
      "medium": 25,
      "low": 45
    },
    "churn_by_contract": {
      "Month-to-month": 25,
      "One year": 3,
      "Two year": 2
    },
    "churn_by_internet_service": {
      "Fiber optic": 18,
      "DSL": 10,
      "No": 2
    },
    "churn_by_payment_method": {
      "Electronic check": 15,
      "Mailed check": 8,
      "Credit card (automatic)": 7
    },
    "average_tenure_churn": 8.5,
    "average_tenure_no_churn": 35.2,
    "monthly_charges_distribution": {
      "min": 18.25,
      "max": 118.75,
      "avg": 64.50
    }
  }
}
```

### 3. Overview Data for Visualization
**Endpoint:** `GET /upload/overview`
**Description:** Get aggregated data for dashboard visualizations and pie charts

**Response:**
```json
{
  "total_customers": 1000,
  "churn_risk": {
    "high": 300,
    "medium": 250,
    "low": 450
  },
  "churn_by_contract": {
    "Month-to-month": 250,
    "One year": 30,
    "Two year": 20
  },
  "churn_by_internet_service": {
    "Fiber optic": 180,
    "DSL": 100,
    "No": 20
  },
  "churn_by_payment_method": {
    "Electronic check": 150,
    "Mailed check": 80,
    "Credit card (automatic)": 70
  },
  "average_tenure_churn": 8.5,
  "average_tenure_no_churn": 35.2,
  "monthly_charges_distribution": {
    "min": 18.25,
    "max": 118.75,
    "avg": 64.50
  }
}
```

### 4. CSV Download with Results
**Endpoint:** `POST /upload/download`
**Description:** Upload CSV file and download processed results with churn probabilities, reasons, and recommendations

**Request:**
- Content-Type: `multipart/form-data`
- File: CSV file with customer data

**Response:** 
- Content-Type: `text/csv`
- File download: `churn_analysis_results.csv`

**Downloaded CSV Format:**
The downloaded CSV includes all original columns plus:
- `Churn_Probability`: Probability score (0-1)
- `Churn_Prediction`: "Yes" or "No"
- `Churn_Reason`: Primary reason for churn risk
- `Recommendations`: Semicolon-separated list of recommendations

## Churn Risk Categories
- **High Risk**: Probability > 0.7 (Immediate intervention required)
- **Medium Risk**: Probability 0.4-0.7 (Monitor and engage)
- **Low Risk**: Probability < 0.4 (Regular engagement)

## Common Churn Reasons
1. High monthly charges (> $80)
2. Short customer tenure (< 12 months)
3. Month-to-month contracts
4. Fiber optic internet service
5. Lack of technical support
6. Electronic check payment method
7. No online security
8. Paperless billing

## Recommendation Types
- **Pricing**: Discounts, promotional offers, cost optimization
- **Contract**: Long-term incentives, annual plan benefits
- **Support**: Free trials, proactive outreach
- **Service**: Quality reviews, upgrades, optimization
- **Payment**: Auto-pay discounts, electronic payment setup
- **Engagement**: Targeted campaigns, activity monitoring

## Model Information
The system automatically selects the best performing model between:
- Logistic Regression
- XGBoost

Model selection is based on accuracy metrics during training.

## Error Handling
All endpoints return appropriate HTTP status codes:
- `200`: Success
- `400`: Bad request (invalid file format, missing columns)
- `401`: Unauthorized (missing/invalid token)
- `404`: User not found
- `500`: Internal server error (processing failure)

## Usage Example

### Frontend Integration
```javascript
// Upload CSV and get results
const formData = new FormData();
formData.append('file', csvFile);

const response = await fetch('/upload', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});

const data = await response.json();

// Use overview data for visualizations
updatePieCharts(data.overview.churn_risk);
updateBarCharts(data.overview.churn_by_contract);
```

### Download Results
```javascript
// Upload and download processed results
const formData = new FormData();
formData.append('file', csvFile);

const response = await fetch('/upload/download', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});

const blob = await response.blob();
const url = window.URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'churn_analysis_results.csv';
a.click();
```

## Data Privacy
- All predictions are stored in the database associated with the user account
- Temporary files are automatically cleaned up after download
- Customer data is processed securely with proper authentication
