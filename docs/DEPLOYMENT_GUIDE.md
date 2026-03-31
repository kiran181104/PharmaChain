# Railway Deployment Guide

## 🚀 Deploy to Railway

### Prerequisites
- Railway account (with active billing plan)
- MongoDB Atlas account (free tier)
- Infura account (for blockchain provider)

### Step 1: Setup MongoDB Atlas
1. Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create a free cluster
3. Create a database user
4. Get the connection string: `mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority`

### Step 2: Setup Infura (Blockchain Provider)
1. Go to [Infura.io](https://infura.io)
2. Create a free account
3. Create a new project for Sepolia testnet
4. Get your Project ID

### Step 3: Deploy Backend to Railway
1. Go to [Railway.app](https://railway.app)
2. Connect your GitHub repository
3. Railway will detect the `railway.json` and `Dockerfile`
4. Go to Variables tab and add:

```
MONGODB_URL=mongodb+srv://your_atlas_connection_string
MONGODB_DB_NAME=drug_traceability
BLOCKCHAIN_PROVIDER_URL=https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID
CONTRACT_ADDRESS=0x5B3fB8Fff9A2A5b5956D8e920047d139ceCAf85D
PRIVATE_KEY=your_private_key_for_contract_owner
CORS_ORIGINS=["https://your-frontend.vercel.app"]
SECRET_KEY=generate_random_string_32_chars
```

### Step 4: Deploy Frontend to Vercel
1. Go to [Vercel.com](https://vercel.com)
2. Connect your GitHub repository
3. Set build command: `npm run build`
4. Add environment variables:
```
REACT_APP_API_URL=https://your-railway-backend.up.railway.app
```

### Step 5: Update CORS
After deployment, update the `CORS_ORIGINS` in Railway with your Vercel frontend URL.

## 🔧 Environment Variables Reference

### Required for Backend
- `MONGODB_URL`: MongoDB Atlas connection string
- `MONGODB_DB_NAME`: Database name (default: drug_traceability)
- `BLOCKCHAIN_PROVIDER_URL`: Infura or other Web3 provider URL
- `CONTRACT_ADDRESS`: Deployed smart contract address
- `PRIVATE_KEY`: Private key for contract owner (keep secure!)
- `CORS_ORIGINS`: JSON array of allowed frontend URLs
- `SECRET_KEY`: Random string for JWT signing

### Optional
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)

## 🔧 Troubleshooting

### Backend not starting
- Check Railway logs for database connection errors
- Ensure MongoDB Atlas IP whitelist includes `0.0.0.0/0`
- Verify environment variables are set correctly
- Check that `BLOCKCHAIN_PROVIDER_URL` is accessible

### Frontend can't connect to backend
- Check `REACT_APP_API_URL` is set to Railway backend URL
- Ensure CORS_ORIGINS includes your frontend domain
- Test backend health endpoint: `https://your-backend.up.railway.app/health`

### Blockchain connection issues
- Backend will start even if blockchain is unavailable
- API calls will work with database-only mode
- Check Infura project ID and network (Sepolia testnet)
- Verify contract address is correct

### Database connection issues
- Backend will start even if MongoDB is unavailable
- API calls will return 503 Service Unavailable
- Check MongoDB Atlas network access and credentials

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
