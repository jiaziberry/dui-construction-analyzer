# Deploy Production Version with Full V70 Classifier

## 🎯 Goal
Replace the buggy simple classifier with the **full V70 production classifier** (~95% accuracy!)

---

## 📁 Files You Need to Upload

You need to upload **3 files** to GitHub:

1. **dui_web_app_v2_production.py** - Main app (with V70 integration)
2. **dui_classifier_v70_lite.py** - The V70 classifier (rule-based only)
3. **requirements_production.txt** - Dependencies (rename to requirements_webapp.txt)

---

## 🚀 Step-by-Step Deployment

### Step 1: Delete Old Files from GitHub

1. Go to your repository: `https://github.com/YOUR-USERNAME/dui-construction-analyzer`
2. Delete these old files (click file → trash icon):
   - ❌ `dui_web_app.py` (old buggy version)
   - ❌ `requirements_webapp.txt` (old requirements)

---

### Step 2: Upload New Files

1. Click **"Add file"** → **"Upload files"**

2. Upload these **3 files** (in this order):
   
   **File 1**: `dui_classifier_v70_lite.py`
   - This is the V70 classifier
   - Size: ~2000 lines (that's OK!)
   - Upload first
   
   **File 2**: `dui_web_app_v2_production.py`
   - This is the new app
   - Upload second
   
   **File 3**: `requirements_production.txt`
   - Upload third
   - **IMPORTANT**: After upload, RENAME it to `requirements_webapp.txt`

3. Scroll down, commit message: "Add production version with V70 classifier"

4. Click **"Commit changes"**

---

### Step 3: Rename Files (Important!)

After uploading, you need to rename 2 files:

**Rename 1**: `dui_web_app_v2_production.py` → `dui_web_app.py`
1. Click on `dui_web_app_v2_production.py`
2. Click pencil icon (edit)
3. At the top, change filename to: `dui_web_app.py`
4. Scroll down, commit: "Rename to dui_web_app.py"

**Rename 2**: `requirements_production.txt` → `requirements_webapp.txt`
1. Click on `requirements_production.txt`
2. Click pencil icon
3. Change filename to: `requirements_webapp.txt`
4. Commit: "Rename to requirements_webapp.txt"

---

### Step 4: Update Streamlit Cloud (if needed)

1. Go to https://share.streamlit.io
2. Click your app
3. Click **"⚙️ Settings"**
4. Check "Main file path" is: `dui_web_app.py` ✅
5. Click **"Reboot app"**
6. Wait 2-3 minutes

---

### Step 5: Test the Fixed App!

1. Go to your app URL
2. Enter: `他对我很坏`
3. Click "Analyze"
4. **Should show**: DISP (Disposition) - 94% ✅
5. **NOT**: ABT ❌

Try other examples:
- `我对他很了解` → Should be MS (93%)
- `专家对问题进行研究` → Should be SI (94%)

---

## ✅ What's Different in Production Version?

### V1 (Old - Buggy):
- ❌ Simple hardcoded lists
- ❌ Only ~50 predicates
- ❌ No pattern detection
- ❌ ~50% accuracy
- ❌ 他对我很坏 → ABT (WRONG!)

### V2 (New - Production):
- ✅ Full V70 classifier
- ✅ 2000+ lines of rules
- ✅ Pattern detection (很+adj, 是+comp, etc.)
- ✅ Name recognition
- ✅ ~95% accuracy
- ✅ 他对我很坏 → DISP (CORRECT!)

---

## 📊 File Sizes

Don't worry about file sizes - these are totally fine for GitHub and Streamlit:

- `dui_web_app.py`: ~20 KB ✅
- `dui_classifier_v70_lite.py`: ~80 KB ✅ (This is the full classifier!)
- `requirements_webapp.txt`: 1 KB ✅

**Total**: ~100 KB (GitHub limit is 100 MB, so we're fine!)

---

## 🔍 Verify Upload Worked

After uploading, your repository should have these files:

```
dui-construction-analyzer/
├── README.md
├── dui_web_app.py (new production version)
├── dui_classifier_v70_lite.py (the V70 classifier)
├── requirements_webapp.txt (new requirements)
└── other files...
```

Check GitHub - do you see all 3 files? ✅

---

## ⚡ Expected Results

### Before (Simple Classifier):
```
他对我很坏 → ABT (70%) ❌
对他很了解 → ABT (92%) ❌
她对我很好 → ABT (70%) ❌

Accuracy: ~50-60%
```

### After (V70 Classifier):
```
他对我很坏 → DISP (94%) ✅
对他很了解 → MS (93%) ✅
她对我很好 → DISP (94%) ✅

Accuracy: ~95%
```

---

## 🆘 Troubleshooting

### "Import Error: dui_classifier_v70_lite"

**Problem**: App can't find the classifier file

**Solution**:
1. Check `dui_classifier_v70_lite.py` exists in your repository
2. Check spelling is EXACT (case-sensitive!)
3. Make sure both files are in the same directory (root of repo)

---

### "Still Showing ABT"

**Solutions** (try in order):
1. Wait 3-5 minutes (deployment takes time)
2. Force refresh: Ctrl+F5 (Windows) or Cmd+Shift+R (Mac)
3. Open in incognito/private mode
4. Go to Streamlit → Reboot app
5. Check GitHub - are the NEW files there?

---

### "Too Many Files"

**You should ONLY have these main files**:
- ✅ dui_web_app.py (new)
- ✅ dui_classifier_v70_lite.py (new)
- ✅ requirements_webapp.txt (new)
- ✅ README.md (original)

**Delete these if they exist**:
- ❌ Any file with "v2_production" in the name (after renaming)
- ❌ Old dui_web_app.py (if you see multiple versions)

---

## 📝 Quick Checklist

Before testing:

- [ ] Deleted old `dui_web_app.py`
- [ ] Uploaded `dui_classifier_v70_lite.py`
- [ ] Uploaded `dui_web_app_v2_production.py`
- [ ] Renamed `dui_web_app_v2_production.py` → `dui_web_app.py`
- [ ] Uploaded `requirements_production.txt`
- [ ] Renamed `requirements_production.txt` → `requirements_webapp.txt`
- [ ] Streamlit redeployed (waited 3 minutes)
- [ ] Tested with `他对我很坏`
- [ ] Shows DISP not ABT ✅

---

## 🎉 Success Indicators

You'll know it worked when:

1. ✅ App shows: "Using V70 Production Classifier (High Accuracy)" at the top
2. ✅ `他对我很坏` → DISP (94%)
3. ✅ Confidence scores are higher (90-95%)
4. ✅ Classification reasons are detailed (e.g., "很+adjective=manner pattern")

---

## 💡 Pro Tips

1. **Upload in order**: Classifier first, then app, then requirements
2. **Rename after upload**: Don't rename before uploading (confusing)
3. **Wait patiently**: Streamlit takes 2-5 minutes to deploy
4. **Test thoroughly**: Try all 6 example sentences
5. **Use incognito**: Avoids cache issues

---

## 📞 Need Help?

If you get stuck:

1. Take a screenshot of GitHub (showing your files)
2. Take a screenshot of Streamlit error (if any)
3. Tell me what step you're on
4. I'll help you fix it!

---

**Ready to deploy?** Start with Step 1: Delete old files! 🚀

**Expected time**: 10-15 minutes total
