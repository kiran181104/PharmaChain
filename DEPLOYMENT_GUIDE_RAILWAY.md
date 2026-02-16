# Backend Deployment Guide - Railway

## Prerequisites
- GitHub account with repo pushed
- Railway account (free at railway.app)
- MongoDB Atlas account (free tier at mongodb.com/cloud/atlas)

---

## Step 1: Set Up MongoDB Atlas (Cloud Database)

Your local MongoDB won't be accessible from Railway. Use MongoDB Atlas instead:

1. Go to [mongodb.com/cloud/atlas](https://mongodb.com/cloud/atlas)
2. Create free account and cluster
3. **Get Connection String**:
   - Click "Connect" → "Drivers" 
   - Copy the connection string: `mongodb+srv://username:password@cluster.mongodb.net/drug_traceability?retryWrites=true&w=majority`
4. Replace `username` and `password` with your credentials
5. **Add IP Whitelist**: Click "Network Access" → "Add IP Address" → "Allow from anywhere" (for testing)

---

## Step 2: Deploy to Railway

### 2.1 Connect GitHub Repository

1. Go to [railway.app](https://railway.app) and sign up
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your GitHub repository: `kiran181104/PharmaChain`
4. Railway will auto-detect it's a Python project

### 2.2 Configure Environment Variables

After Railway detects your project:

1. Click **"Variables"** tab
2. Add these environment variables:

```
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/drug_traceability?retryWrites=true&w=majority
MONGODB_DB_NAME=drug_traceability
BLOCKCHAIN_PROVIDER_URL=http://127.0.0.1:7545
CONTRACT_ADDRESS=0xB6694411E52905a060173FCc3D9783084dA3964B
PRIVATE_KEY=0x992e98ff8098a6b23e96e8b8b2a49ddc020264c34580362bc3a2d406cf13577e
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000", "https://drug-traceablity-system.vercel.app", "https://YOUR-RAILWAY-DOMAIN.railway.app"]
SECRET_KEY=your-secure-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

⚠️ **Important**: 
- Replace `username:password` in MongoDB URL with your Atlas credentials
- Once deployed, Railway will show your domain URL - add it to CORS_ORIGINS

### 2.3 Deploy

1. Railway will automatically deploy when you push to GitHub
2. Wait 2-3 minutes for deployment to complete
3. Click **"View Logs"** to monitor deployment

### 2.4 Get Your Backend URL

1. Click **"Settings"** → **"Domains"**
2. Copy the generated domain: `https://your-railway-domain.railway.app`
3. **This is your new API_URL for the frontend!**

---

## Step 3: Update and Redeploy Frontend

### 3.1 Update Frontend Environment Variables

Update `frontend/.env`:

```dotenv
REACT_APP_API_URL=https://your-railway-domain.railway.app
REACT_APP_CONTRACT_ADDRESS=0xB6694411E52905a060173FCc3D9783084dA3964B
REACT_APP_BLOCKCHAIN_NETWORK_ID=5777
```

### 3.2 Commit and Push

```bash
git add frontend/.env
git commit -m "Update backend API URL for production"
git push origin main
```

### 3.3 Redeploy on Vercel

Vercel watches your GitHub repo, so:
1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Your project should auto-redeploy when you push
3. Wait for deployment to complete
4. Access your app at `https://drug-traceablity-system.vercel.app`

---

## Step 4: Test the Deployment

1. Open your frontend: `https://drug-traceablity-system.vercel.app`
2. Try to register a user
3. Check browser DevTools for CORS errors (should be none)
4. Verify requests go to your Railway backend

---

## Troubleshooting

### Issue: 502 Bad Gateway
- Check Railway logs: Click "View Logs"
- Ensure MongoDB connection string is correct
- Check all required env variables are set

### Issue: CORS Error Still Appears
- Update `CORS_ORIGINS` in Railway Variables with your actual Railway domain
- Restart deployment: Click "Redeploy" in Railway

### Issue: Blockchain Connection Error
- Ganache must still be running locally on your machine where tests happen
- For production blockchain, use TestNet or MainNet (requires setup)

### Issue: Database Not Connecting
- Verify MongoDB Atlas connection string
- Check IP whitelist allows Railway's IPs (use "Allow from anywhere")
- Test connection string locally first

---

## Important Notes

⚠️ **Blockchain Limitation**: 
- Your smart contract is deployed to local Ganache
- Railway backend can't access your local Ganache
- **Solutions**:
  1. Deploy to Ganache hosted service (e.g., Alchemy)
  2. Use test network (Sepolia, etc.)
  3. Keep blockchain local, use backend for blockchain interactions only

For now, ensure blockchain interactions work with your setup and document this limitation.

---

## Next Steps

1. ✅ Push code to GitHub
2. ✅ Deploy backend to Railway
3. ✅ Set up MongoDB Atlas
4. ✅ Update frontend environment variables
5. ✅ Redeploy frontend
6. ✅ Test the complete system
