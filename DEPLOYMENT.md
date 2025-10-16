# Deployment Guide - Road Explorer Portugal

**Version:** 1.0.0
**Date:** 2025-10-16
**Platform:** Vercel

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Vercel Deployment](#vercel-deployment)
4. [Environment Variables](#environment-variables)
5. [Post-Deployment Verification](#post-deployment-verification)
6. [Troubleshooting](#troubleshooting)
7. [Rollback Procedures](#rollback-procedures)

---

## Prerequisites

### Required Accounts
- ✅ **Vercel Account** - Sign up at [vercel.com](https://vercel.com/)
- ✅ **GitHub Account** - Repository must be on GitHub
- ✅ **Mapbox Account** - Get token at [mapbox.com](https://account.mapbox.com/)
- ✅ **Supabase Account** - Get credentials at [supabase.com](https://app.supabase.com/)

### Local Requirements
- ✅ Node.js 18+
- ✅ npm 9+
- ✅ Git
- ✅ Vercel CLI (optional): `npm install -g vercel`

---

## Pre-Deployment Checklist

### 1. Build Verification
```bash
cd frontend
npm run build
```

**Expected Output:**
- ✅ Build completes successfully
- ✅ `dist/` folder created
- ✅ Total size ~2MB (568KB gzipped)
- ✅ No console errors

### 2. Code Quality
```bash
npm run lint
```

**Expected Output:**
- ✅ No ESLint errors
- ✅ No ESLint warnings (critical ones)

### 3. Configuration Files
- ✅ `frontend/vercel.json` exists
- ✅ `frontend/.env.example` has all required variables
- ✅ `frontend/package.json` has correct scripts

### 4. Git Status
```bash
git status
```

**Expected Output:**
- ✅ All changes committed
- ✅ No uncommitted files
- ✅ On `main` branch

---

## Vercel Deployment

### Method 1: Vercel Dashboard (Recommended for First Deploy)

#### Step 1: Import Project

1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click **"Add New Project"**
3. Click **"Import Git Repository"**
4. Select your GitHub repository
5. Click **"Import"**

#### Step 2: Configure Project

**Framework Preset:** Vite
**Root Directory:** `frontend`
**Build Command:** `npm run build`
**Output Directory:** `dist`
**Install Command:** `npm install`

**Important:** Make sure to set the **Root Directory** to `frontend` since the React app is in a subdirectory.

#### Step 3: Add Environment Variables

Click **"Environment Variables"** and add:

| Key | Value | Source |
|-----|-------|--------|
| `VITE_MAPBOX_TOKEN` | `pk.your_mapbox_token` | [Mapbox Dashboard](https://account.mapbox.com/access-tokens/) |
| `VITE_SUPABASE_URL` | `https://xxx.supabase.co` | [Supabase Settings → API](https://app.supabase.com/project/_/settings/api) |
| `VITE_SUPABASE_ANON_KEY` | `your_anon_key` | [Supabase Settings → API](https://app.supabase.com/project/_/settings/api) |

**Security Note:**
- Use **ANON KEY** (not service role key) for frontend
- These values will be included in client-side bundle (this is expected)
- Supabase RLS policies protect your data

#### Step 4: Deploy

1. Click **"Deploy"**
2. Wait 2-3 minutes for build
3. Vercel will provide a live URL: `https://road-explorer-portugal.vercel.app`

---

### Method 2: Vercel CLI (For Subsequent Deploys)

#### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

#### Step 2: Login
```bash
vercel login
```

#### Step 3: Link Project (First Time Only)
```bash
cd frontend
vercel link
```

Follow prompts:
- Scope: Select your account
- Link to existing project: Yes (if already created via dashboard)
- Project: road-explorer-portugal

#### Step 4: Deploy to Production
```bash
vercel --prod
```

**Expected Output:**
```
✓ Production: https://road-explorer-portugal.vercel.app [2m]
```

---

## Environment Variables

### Required Variables

#### 1. VITE_MAPBOX_TOKEN
**Purpose:** Mapbox GL JS map rendering
**Get it:** [Mapbox Access Tokens](https://account.mapbox.com/access-tokens/)
**Format:** `pk.eyJ1...` (starts with `pk.`)
**Scopes Required:** Public (default)
**Free Tier:** 50,000 map loads/month

#### 2. VITE_SUPABASE_URL
**Purpose:** Supabase database connection
**Get it:** Supabase Dashboard → Settings → API → Project URL
**Format:** `https://xxxxxxxxxxxxx.supabase.co`
**Note:** Copy exact URL including `https://`

#### 3. VITE_SUPABASE_ANON_KEY
**Purpose:** Supabase anonymous/public access
**Get it:** Supabase Dashboard → Settings → API → Project API keys → anon (public)
**Format:** Long alphanumeric string (100+ characters)
**Security:** Safe to expose in frontend (protected by RLS policies)

### Setting Environment Variables in Vercel

**Via Dashboard:**
1. Go to Project Settings → Environment Variables
2. Add each variable
3. Environment: Production, Preview, Development (select all)
4. Click "Save"
5. Redeploy to apply changes

**Via CLI:**
```bash
vercel env add VITE_MAPBOX_TOKEN production
# Paste value when prompted
```

---

## Post-Deployment Verification

### Production Checklist

Visit your live URL and verify:

#### Functionality Tests
- [ ] **Page loads** - No errors, shows header and map
- [ ] **Road list loads** - Sidebar shows 12+ roads
- [ ] **Search works** - Type "N222" → filters correctly
- [ ] **Region filter works** - Click Continental → filters correctly
- [ ] **Road selection** - Click road → map displays animated route
- [ ] **Route animation** - Route draws smoothly (~2.5s)
- [ ] **Details panel** - Shows metrics (distance, curves, elevation)
- [ ] **GPX export** - Click "Export GPX" → file downloads
- [ ] **Google Maps link** - Click "Google Maps" → opens in new tab
- [ ] **Mobile responsive** - Test on phone (hamburger menu, bottom sheet)

#### Technical Tests
- [ ] **No console errors** - Open DevTools Console → should be clean
- [ ] **Map renders** - Mapbox tiles load correctly
- [ ] **Supabase connection** - Roads data loads from database
- [ ] **HTTPS enabled** - URL shows padlock icon
- [ ] **Fast load time** - Page loads in <2s on 3G

#### Browser Compatibility
Test on:
- [ ] Chrome (desktop)
- [ ] Firefox (desktop)
- [ ] Safari (desktop)
- [ ] Safari (iPhone)
- [ ] Chrome (Android)

#### Performance Audit (Optional)
```bash
# Use Lighthouse in Chrome DevTools
# Go to: DevTools → Lighthouse → Analyze page load
```

**Target Scores:**
- Performance: >90
- Accessibility: >90
- Best Practices: >90
- SEO: >80

---

## Troubleshooting

### Common Issues

#### Issue 1: Build Fails - "Module not found"
**Cause:** Missing dependencies
**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

#### Issue 2: Map Not Rendering
**Cause:** Invalid or missing Mapbox token
**Symptoms:** Gray map area, console error "Invalid token"
**Solution:**
1. Verify `VITE_MAPBOX_TOKEN` in Vercel environment variables
2. Check token is valid at [Mapbox Dashboard](https://account.mapbox.com/access-tokens/)
3. Ensure token has "Public" scopes enabled
4. Redeploy after fixing

#### Issue 3: No Roads Data
**Cause:** Supabase connection issue
**Symptoms:** Empty sidebar, "Failed to load roads" error
**Solution:**
1. Check `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY`
2. Verify Supabase database has roads table with data
3. Check RLS policies allow anonymous read access
4. Test query in Supabase SQL Editor:
   ```sql
   SELECT * FROM roads LIMIT 1;
   ```

#### Issue 4: 404 on Page Refresh
**Cause:** SPA routing not configured
**Symptoms:** Refreshing `/road/123` shows 404
**Solution:**
1. Verify `frontend/vercel.json` exists
2. Check `vercel.json` has rewrite rule for SPA routing
3. Redeploy

#### Issue 5: Security Headers Missing
**Cause:** vercel.json not applied
**Solution:**
1. Check file location: `frontend/vercel.json` (not root)
2. Verify JSON syntax is valid
3. Redeploy

#### Issue 6: Slow Load Time
**Cause:** Bundle size or network issues
**Solutions:**
- Enable gzip/brotli compression (automatic in Vercel)
- Check bundle size: should be ~568KB gzipped
- Use Vercel Analytics to identify bottlenecks

---

## Rollback Procedures

### Method 1: Instant Rollback (Vercel Dashboard)

1. Go to Vercel Dashboard → Deployments
2. Find previous successful deployment
3. Click "⋯" → "Promote to Production"
4. Confirm rollback
5. **Result:** Instant rollback (~10 seconds)

### Method 2: Git Revert + Redeploy

```bash
# Find last good commit
git log --oneline -10

# Revert to specific commit
git revert <commit-hash>

# Push to trigger new deployment
git push origin main
```

### Method 3: Emergency Disable

If critical issue discovered:
1. Vercel Dashboard → Project Settings
2. Pause Deployments (temporarily)
3. Fix issue locally
4. Test thoroughly
5. Resume deployments

---

## Production Deployment Summary

**Status:** ✅ Production-Ready
**Build:** Successful (2.0MB dist, 568KB gzipped)
**Configuration:** Complete (vercel.json with security headers)
**Environment Variables:** 3 required (Mapbox + Supabase)
**Platform:** Vercel (automatic HTTPS, CDN, zero-downtime)
**Estimated Deploy Time:** 2-3 minutes
**Monthly Cost:** $0 (free tier)

---

## Support & Resources

### Documentation
- **Vercel Docs:** https://vercel.com/docs
- **Vite Docs:** https://vitejs.dev/
- **Mapbox GL JS:** https://docs.mapbox.com/mapbox-gl-js/
- **Supabase Docs:** https://supabase.com/docs

### Internal Docs
- `README.md` - Setup instructions
- `context/PRD.md` - Product requirements
- `CLAUDE.md` - Development guidelines
- `frontend/vercel.json` - Deployment configuration

### Monitoring
- **Vercel Analytics:** Project → Analytics (free tier: 1k events/day)
- **Browser Console:** Check for runtime errors
- **Supabase Dashboard:** Monitor database queries and usage

---

**Document Version:** 1.0.0
**Last Updated:** 2025-10-16
**Next Review:** After first production deploy
