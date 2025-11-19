# Flask Vercel Deployment Instructions

## Prerequisites
1. Vercel account (https://vercel.com)
2. GitHub account with the repository connected to Vercel

## Deployment Steps

### Option 1: Using Vercel Dashboard
1. Go to https://vercel.com/dashboard
2. Click "New Project"
3. Import your GitHub repository `badboygamingph/flask-vercel-deployment`
4. Set the project name to `flask-vercel-deployment-amber`
5. Configure the build settings:
   - Build Command: `pip install -r backend/requirements.txt`
   - Output Directory: Leave empty
   - Install Command: Leave empty
6. Click "Deploy"

### Option 2: Using Vercel CLI
1. Install Vercel CLI: `npm install -g vercel`
2. Navigate to your project directory
3. Run: `vercel --prod`
4. Follow the prompts to deploy to production

## Configuration Details
- The Flask app entry point is `backend/flask_app.py`
- Dependencies are in `backend/requirements.txt`
- Vercel configuration is in `vercel.json`

## Custom Domain Setup
To use the URL https://flask-vercel-deployment-amber.vercel.app/:

1. In Vercel Dashboard, go to your project
2. Click "Settings" tab
3. Click "Domains" in the sidebar
4. Add domain: `flask-vercel-deployment-amber.vercel.app`

Note: This domain should be automatically assigned if your project name is `flask-vercel-deployment-amber`.