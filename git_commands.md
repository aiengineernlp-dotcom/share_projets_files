### Refresh Git Index after `.gitignore` modification

If you modified your `.gitignore` but Git is still tracking files that should be ignored, run this sequence of commands:

1. **Commit your current work** (to avoid losing changes):
   ```bash
   git add .
   git commit -m "Save work before gitignore refresh"
   ```

2. **Remove everything from the Git index** (this does NOT delete your physical files):
   ```bash
   git rm -r --cached .
   ```

3. **Re-add all files** (Git will now apply the new `.gitignore` rules):
   ```bash
   git add .
   ```

4. **Commit the changes**:
   ```bash
   git commit -m "Fix: apply new .gitignore rules"
   ```

5. **Push to GitHub**:
   ```bash
   git push origin main
   ```
   *(Replace `main` with your specific branch name if different)*
