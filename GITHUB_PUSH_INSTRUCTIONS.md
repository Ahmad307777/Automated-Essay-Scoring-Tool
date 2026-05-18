# 🚀 How to Push to GitHub

Your project is ready to push! Follow these steps:

## ✅ Step 1: Create GitHub Repository

1. Go to https://github.com
2. Click the **"+"** icon (top right) → **"New repository"**
3. Fill in:
   - **Repository name**: `essay-scoring-nlp` (or your choice)
   - **Description**: `Automated Essay Scoring System using BERT and BiLSTM`
   - **Visibility**: Choose Public or Private
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
4. Click **"Create repository"**

## ✅ Step 2: Connect Local Repository to GitHub

After creating the repository, GitHub will show you commands. Use these:

```bash
# Add the remote repository
git remote add origin https://github.com/YOUR_USERNAME/essay-scoring-nlp.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

**Replace `YOUR_USERNAME`** with your actual GitHub username!

## ✅ Step 3: Verify Upload

1. Refresh your GitHub repository page
2. You should see all your files uploaded!
3. The README will be displayed automatically

---

## 🔧 Alternative: Using GitHub Desktop

If you prefer a GUI:

1. Download GitHub Desktop: https://desktop.github.com
2. Open GitHub Desktop
3. File → Add Local Repository → Select `D:\NLP\essay_scoring`
4. Click "Publish repository"
5. Choose name and visibility
6. Click "Publish"

---

## 📝 Quick Commands Reference

```bash
# Check current status
git status

# Add new files
git add .

# Commit changes
git commit -m "Your commit message"

# Push to GitHub
git push

# Pull latest changes
git pull

# View commit history
git log --oneline
```

---

## ⚠️ Important Notes

### Files Excluded (in .gitignore):
- ✅ Large model files (*.pt, *.pth) - Already excluded
- ✅ Dataset files (*.tsv) - Too large for GitHub
- ✅ Python cache (__pycache__/)
- ✅ Kaggle credentials

### Files Included:
- ✅ All source code (src/, app/)
- ✅ Training scripts
- ✅ Documentation (README, reports)
- ✅ Model metrics (JSON files)
- ✅ Requirements.txt

### Large Files Warning:
If you get an error about large files, you may need to:
1. Remove them from git: `git rm --cached filename`
2. Add to .gitignore
3. Commit and push again

---

## 🎯 After Pushing

### Update README
1. Edit `README_GITHUB.md` on GitHub
2. Replace `YOUR_USERNAME` with your actual username
3. Add your contact information
4. Commit changes

### Add Topics/Tags
On your GitHub repo page:
- Click the gear icon next to "About"
- Add topics: `nlp`, `deep-learning`, `bert`, `lstm`, `essay-scoring`, `pytorch`, `flask`

### Enable GitHub Pages (Optional)
If you want to host documentation:
1. Settings → Pages
2. Source: Deploy from branch
3. Branch: main, folder: /docs
4. Save

---

## 🔐 Authentication

If GitHub asks for credentials:

### Option 1: Personal Access Token (Recommended)
1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Select scopes: `repo` (full control)
4. Copy the token
5. Use token as password when pushing

### Option 2: SSH Key
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copy public key
cat ~/.ssh/id_ed25519.pub

# Add to GitHub: Settings → SSH and GPG keys → New SSH key
```

Then use SSH URL:
```bash
git remote set-url origin git@github.com:YOUR_USERNAME/essay-scoring-nlp.git
```

---

## ✅ Verification Checklist

After pushing, verify:
- [ ] All source files are visible
- [ ] README displays correctly
- [ ] requirements.txt is present
- [ ] Documentation files are included
- [ ] No sensitive data (API keys, passwords)
- [ ] .gitignore is working (no __pycache__, *.pt files)

---

## 🎉 Success!

Once pushed, your repository URL will be:
```
https://github.com/YOUR_USERNAME/essay-scoring-nlp
```

Share this link in your assignment submission!

---

## 📞 Troubleshooting

### Error: "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/essay-scoring-nlp.git
```

### Error: "failed to push some refs"
```bash
git pull origin main --rebase
git push origin main
```

### Error: "large files"
```bash
# Find large files
find . -type f -size +50M

# Remove from git
git rm --cached path/to/large/file

# Add to .gitignore and commit
```

---

**Need help?** Check GitHub's documentation: https://docs.github.com/en/get-started
