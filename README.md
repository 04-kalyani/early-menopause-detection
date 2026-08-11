# Menopause Detection & Diet Recommendation Platform

A comprehensive, production-ready platform for early menopause prediction using machine learning and personalized diet recommendations.

## About This Project

This platform provides early prediction of menopause based on various physiological and psychological indicators using advanced machine learning techniques. It combines multiple ML models (LDA, QDA, Random Forest) into a Super Learner ensemble for accurate predictions, and offers personalized diet recommendations based on user symptoms and health profile.

### Key Features

- **Early Menopause Prediction**: Predicts menopause status using age, symptoms, hormone levels, and lifestyle factors
- **Multiple ML Models**: Linear Discriminant Analysis (LDA), Quadratic Discriminant Analysis (QDA), Random Forest, and Super Learner ensemble
- **LASSO Feature Selection**: Identifies the most significant predictors
- **Personalized Diet Recommendations**: Tailored dietary suggestions based on symptoms and predictions
- **Professional UI/UX**: Modern, intuitive React interface with clear explanations
- **Robust Backend**: FastAPI-based Python backend with comprehensive error handling

## Tech Stack

### Backend
- **Python 3.8+**: Core programming language
- **FastAPI**: Modern, fast web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI
- **Scikit-learn**: Machine learning models (LDA, QDA, Random Forest)
- **Pandas & NumPy**: Data processing and manipulation
- **Joblib**: Model serialization and loading
- **Imbalanced-learn**: Handling class imbalance in datasets

### Frontend
- **React**: UI library for building user interfaces
- **Material-UI (MUI v5)**: Component library for professional UI/UX
- **Axios**: HTTP client for API communication

### Data Processing
- **Pandas**: Data cleaning and preprocessing
- **NumPy**: Numerical computations
- **Scipy**: Statistical functions
- **Pyreadstat**: Reading SAS/SPSS data files

### Data Sources
- **SWAN**: Study of Women's Health Across the Nation
- **NHANES**: National Health and Nutrition Examination Survey 2013-2014
- **USDA FoodData Central**: Food and nutrient database

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Node.js 14+ and npm
- Datasets placed in `datasets/` folder (SWAN and NHANES data)

### Backend Setup

1. **Create virtual environment:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Train models (required before running API):**
```bash
python data_processing/train_models.py
```

4. **Start API server:**
```bash
cd app
python main.py
# Or use uvicorn directly:
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### Frontend Setup

1. **Install dependencies:**
```bash
cd frontend
npm install
```

2. **Start development server:**
```bash
npm start
```

The frontend will be available at `http://localhost:3000`

### Quick Start (Both Services)

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
cd app && python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

## Project Structure

```
menopause-detection/
├── backend/              # Python FastAPI backend
│   ├── app/             # Main application (API endpoints)
│   ├── models/          # ML model definitions
│   ├── data_processing/ # Data preprocessing pipeline
│   └── requirements.txt  # Python dependencies
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   └── services/    # API services
│   └── package.json    # Frontend dependencies
└── datasets/            # Raw datasets (SWAN, NHANES, USDA)
```

## API Endpoints

- `GET /health` - Health check
- `POST /predict` - Make menopause prediction
- `GET /models/info` - Get model information
- `GET /docs` - Interactive API documentation

## License

[Add your license here]
