# CodeBuddy Deployment Guide

This guide will help you deploy CodeBuddy with separate backend and frontend hosting.

## 🚀 Quick Start

### Option 1: Render.com (Recommended - Free Tier Available)

#### Backend Deployment (Flask API)

1. **Create a new Web Service on Render**
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure the Backend Service**
   - **Name**: `codebuddy-backend`
   - **Root Directory**: `student_code_evaluator/backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Port**: `5000`

3. **Set Environment Variables**
   - `GOOGLE_API_KEY`: Your Google AI API key

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete
   - Note the URL (e.g., `https://codebuddy-backend.onrender.com`)

#### Frontend Deployment (Streamlit)

1. **Update Streamlit Cloud Configuration**
   - Go to your Streamlit Cloud dashboard
   - Navigate to your app settings
   - Add environment variable:
     - **Key**: `BACKEND_URL`
     - **Value**: `https://your-backend-url.onrender.com` (from step 4 above)

2. **Redeploy Frontend**
   - Push your changes to GitHub
   - Streamlit Cloud will automatically redeploy

### Option 2: Railway.app (Alternative - Free Tier Available)

#### Backend Deployment

1. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Deploy Backend**
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Set root directory to `student_code_evaluator/backend`
   - Add environment variable: `GOOGLE_API_KEY`

3. **Get Backend URL**
   - Railway will provide a URL like `https://your-app-name.railway.app`

#### Frontend Deployment

1. **Update Streamlit Cloud**
   - Add environment variable `BACKEND_URL` with your Railway backend URL
   - Redeploy

### Option 3: Heroku (Paid)

#### Backend Deployment

1. **Create Heroku App**
   ```bash
   heroku create codebuddy-backend
   ```

2. **Deploy Backend**
   ```bash
   cd student_code_evaluator/backend
   heroku git:remote -a codebuddy-backend
   git add .
   git commit -m "Deploy backend"
   git push heroku main
   ```

3. **Set Environment Variables**
   ```bash
   heroku config:set GOOGLE_API_KEY=your_api_key
   ```

## 🔧 Configuration Files

### For Render.com
Create `render.yaml` in your root directory:

```yaml
services:
  - type: web
    name: codebuddy-backend
    env: python
    rootDir: student_code_evaluator/backend
    buildCommand: pip install -r requirements.txt
    startCommand: python app.py
    envVars:
      - key: GOOGLE_API_KEY
        sync: false
```

### For Railway.app
Create `railway.json` in `student_code_evaluator/backend/`:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python app.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

## 🌐 Environment Variables

### Backend Required Variables
- `GOOGLE_API_KEY`: Your Google AI API key

### Frontend Required Variables
- `BACKEND_URL`: URL of your deployed backend (e.g., `https://codebuddy-backend.onrender.com`)
- `GOOGLE_API_KEY`: Your Google AI API key

## 📝 Testing Your Deployment

1. **Test Backend**
   ```bash
   curl https://your-backend-url.com/health
   ```

2. **Test Frontend**
   - Visit your Streamlit app URL
   - Try uploading a code file and starting evaluation

3. **Use the verification script**
   ```bash
   python verify_deployment.py https://your-backend-url.com
   ```

## 🔗 Final URLs

After deployment, you'll have:
- **Frontend**: `https://codebuddyv1.streamlit.app/` (your existing Streamlit Cloud URL)
- **Backend**: `https://your-backend-url.com` (new backend URL)

## 🛠️ Troubleshooting

### Common Issues

1. **CORS Errors**
   - Add CORS headers to your Flask backend
   - Update the backend to allow requests from your frontend domain

2. **Database Issues**
   - Ensure the backend has write permissions
   - Check that the database file is being created

3. **Environment Variables**
   - Double-check that all environment variables are set correctly
   - Verify the `BACKEND_URL` points to the correct backend

### Adding CORS Support

If you encounter CORS issues, add this to your Flask backend:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
```

And add `flask-cors` to your `requirements.txt`:

```
flask-cors
```

## 📊 Monitoring

- **Backend Health**: `https://your-backend-url.com/health`
- **Backend API Info**: `https://your-backend-url.com/`

## 🎉 Success!

Once deployed, share your frontend URL with users:
`https://codebuddyv1.streamlit.app/`

The backend will handle all the heavy lifting (database, API calls) while your users interact with the beautiful Streamlit interface! 