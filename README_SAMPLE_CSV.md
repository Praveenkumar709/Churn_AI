# Customer Churn Prediction - Sample CSV Dataset

## Sample CSV File Location
`sample_customer_churn.csv` is located in the root directory: `c:\Users\bayya\OneDrive\Desktop\Cognizant\Website\sample_customer_churn.csv`

## Required CSV Columns
The CSV file must contain the following columns:

- **customer_id**: Unique identifier for each customer
- **gender**: Customer gender (Male/Female)
- **SeniorCitizen**: Whether customer is a senior citizen (0/1)
- **Partner**: Whether customer has a partner (Yes/No)
- **Dependents**: Whether customer has dependents (Yes/No)
- **tenure**: Number of months the customer has been with the company
- **PhoneService**: Whether customer has phone service (Yes/No)
- **MultipleLines**: Whether customer has multiple lines (Yes/No/No phone service)
- **OnlineSecurity**: Whether customer has online security (Yes/No/No internet service)
- **OnlineBackup**: Whether customer has online backup (Yes/No/No internet service)
- **DeviceProtection**: Whether customer has device protection (Yes/No/No internet service)
- **TechSupport**: Whether customer has tech support (Yes/No/No internet service)
- **StreamingTV**: Whether customer has streaming TV (Yes/No/No internet service)
- **StreamingMovies**: Whether customer has streaming movies (Yes/No/No internet service)
- **PaperlessBilling**: Whether customer has paperless billing (Yes/No)
- **MonthlyCharges**: Monthly charges amount
- **TotalCharges**: Total charges amount
- **Contract**: Contract type (Month-to-month/One year/Two year)
- **InternetService**: Internet service type (DSL/Fiber optic/No)
- **PaymentMethod**: Payment method (Electronic check/Mailed check/Bank transfer (automatic)/Credit card (automatic))

## Sample Data Format
```csv
customer_id,gender,SeniorCitizen,Partner,Dependents,tenure,PhoneService,MultipleLines,OnlineSecurity,OnlineBackup,DeviceProtection,TechSupport,StreamingTV,StreamingMovies,PaperlessBilling,MonthlyCharges,TotalCharges,Contract,InternetService,PaymentMethod
CUST001,Female,0,Yes,No,1,No,No phone service,No internet service,No internet service,No internet service,No internet service,No internet service,No internet service,No,29.85,29.85,Month-to-month,No,Electronic check
CUST002,Male,0,No,No,34,Yes,No,Yes,No,Yes,No,No,No,No,Yes,56.95,1889.5,One year,DSL,Electronic check
```

## How to Use
1. **Upload via Frontend**: Use the file upload feature in the frontend application
2. **API Endpoint**: POST to `/upload` with the CSV file
3. **Expected Response**: JSON with predictions, churn probabilities, and recommendations

## Fixes Applied
1. **Fixed validation error**: Changed `churn_by_location` to `churn_by_internet_service` in the predictor to match the schema
2. **Added CSV transformation**: Updated the predictor to handle both CSV format and transformed model format
3. **Enhanced overview generation**: Made the overview data generation compatible with both CSV and transformed data formats
4. **Database migration**: Added `original_data` column to store original customer data for better overview generation
5. **Updated required columns**: Added Contract, InternetService, and PaymentMethod to the required columns list

## Testing
The sample CSV contains 20 customer records with various combinations of features to test different churn prediction scenarios. You can upload this file through the frontend to test the churn prediction functionality.
