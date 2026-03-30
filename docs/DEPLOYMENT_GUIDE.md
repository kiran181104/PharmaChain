# Railway Deployment Guide

## 🚀 Deploy to Railway

### Prerequisites
- Railway account (with active billing plan)
- MongoDB Atlas account (free tier)
- GitHub repository

### Step 1: Setup MongoDB Atlas
1. Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create a free cluster
3. Create a database user
4. Get the connection string: `mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority`

### Step 2: Deploy Backend to Railway
1. Go to [Railway.app](https://railway.app)
2. Connect your GitHub repository
3. Railway will detect the `railway.json` and `Dockerfile`
4. Go to Variables tab and add:

```
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/drug_traceability
MONGODB_DB_NAME=drug_traceability
BLOCKCHAIN_PROVIDER_URL=https://mainnet.infura.io/v3/YOUR_INFURA_KEY
CONTRACT_ADDRESS=0x5B3fB8Fff9A2A5b5956D8e920047d139ceCAf85D
PRIVATE_KEY=your_private_key
CORS_ORIGINS=["https://your-frontend-domain.vercel.app"]
SECRET_KEY=your_random_secret_key
```

### Step 3: Deploy Frontend to Vercel
1. Go to [Vercel.com](https://vercel.com)
2. Connect your GitHub repository
3. Set build command: `npm run build`
4. Add environment variables:
```
REACT_APP_API_URL=https://your-railway-backend-url.up.railway.app
```

### Step 4: Update CORS
After deployment, update the `CORS_ORIGINS` in Railway with your Vercel frontend URL.

## 🔧 Troubleshooting

### Backend not starting
- Check Railway logs for database connection errors
- Ensure MongoDB Atlas IP whitelist includes `0.0.0.0/0`
- Verify environment variables are set correctly

### Frontend can't connect to backend
- Check `REACT_APP_API_URL` is set to Railway backend URL
- Ensure CORS_ORIGINS includes your frontend domain
- Test backend health endpoint: `https://your-backend.up.railway.app/health`

### Database connection issues
- Backend will start even if MongoDB is unavailable
- API calls will return 503 Service Unavailable
- Check MongoDB Atlas network access and credentials
    "drugName": "Metformin 500mg",
    "standardComposition": {
      "ingredients": [
        { "name": "Metformin Hydrochloride", "quantity": "500mg", "percentage": 62.5 },
        { "name": "Povidone", "quantity": "150mg", "percentage": 18.75 },
        { "name": "Microcrystalline Cellulose", "quantity": "100mg", "percentage": 12.5 },
        { "name": "Magnesium Stearate", "quantity": "30mg", "percentage": 3.75 },
        { "name": "Hypromellose", "quantity": "20mg", "percentage": 2.5 }
      ]
    }
  },
  {
    "drugName": "Ciprofloxacin 500mg",
    "standardComposition": {
      "ingredients": [
        { "name": "Ciprofloxacin Hydrochloride", "quantity": "500mg", "percentage": 55.6 },
        { "name": "Microcrystalline Cellulose", "quantity": "200mg", "percentage": 22.2 },
        { "name": "Crospovidone", "quantity": "100mg", "percentage": 11.1 },
        { "name": "Magnesium Stearate", "quantity": "50mg", "percentage": 5.6 },
        { "name": "Colloidal Silicon Dioxide", "quantity": "50mg", "percentage": 5.6 }
      ]
    }
  }
]
