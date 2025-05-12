# AD Security Assessment Tool - Update Guide

This guide provides instructions on how to update your existing AD Security Assessment Tool installation to the latest version from the GitHub repository.

## Prerequisites

- Git installed on your system
- Existing installation of the AD Security Assessment Tool
- Administrator/sudo privileges (for installing dependencies if needed)

## Update Steps

### 1. Backup Your Configuration

Before updating, it's recommended to backup your configuration files:

```bash
# Create a backup of your configuration files
cp config.json config.json.backup
cp auth_config.json auth_config.json.backup
```

### 2. Fetch and Apply Updates

#### For Windows:

```powershell
# Navigate to your project directory
cd path\to\ad-security-assessment

# Fetch the latest changes
git fetch origin

# Check for any changes that might conflict with your local changes
git status

# If you have local changes you want to keep, stash them
git stash

# Pull the latest changes
git pull origin main

# If you stashed changes, apply them back
git stash pop

# If there are conflicts, resolve them manually
# Then commit the resolved conflicts
git add .
git commit -m "Resolved merge conflicts"
```

#### For Linux/macOS:

```bash
# Navigate to your project directory
cd path/to/ad-security-assessment

# Fetch the latest changes
git fetch origin

# Check for any changes that might conflict with your local changes
git status

# If you have local changes you want to keep, stash them
git stash

# Pull the latest changes
git pull origin main

# If you stashed changes, apply them back
git stash pop

# If there are conflicts, resolve them manually
# Then commit the resolved conflicts
git add .
git commit -m "Resolved merge conflicts"
```

### 3. Update Dependencies

After pulling the latest changes, you should update the dependencies:

#### For Windows:

```powershell
# Update Python dependencies
pip install -r requirements.txt --upgrade

# Update frontend dependencies
cd frontend
npm install
cd ..
```

#### For Linux/macOS:

```bash
# Update Python dependencies
pip install -r requirements.txt --upgrade

# Update frontend dependencies
cd frontend
npm install
cd ..
```

### 4. Restart Services

If you have the API server or web UI running, restart them to apply the changes:

#### For Windows:

```powershell
# Stop any running instances (you may need to use Task Manager or other methods)
# Then restart the services
start run_api.py
start run_web_ui.bat
```

#### For Linux/macOS:

```bash
# Stop any running instances
pkill -f "python run_api.py"
pkill -f "python run_web_ui.py"

# Restart the services
./run_api.py &
./run_web_ui.sh &
```

### 5. Verify the Update

1. Open your browser and navigate to the web UI (default: http://localhost:3000)
2. Log in to the application
3. Check that the new features are available:
   - Baseline compliance selection (CIS, STIG, Microsoft Security benchmarks)
   - Remediation steps for failed checks in technical reports
   - Report preview functionality before download
   - Enhanced dashboard with assessment history and trending graph

## Troubleshooting

### ESLint Errors

If you encounter ESLint errors after updating, such as:

```
[eslint]
src\pages\AssessmentResult.js
Line `93:67: React Hook "useState" cannot be called inside a callback, React hooks must be called in a React function component or a custom React Hook function
```

These are typically React hooks usage errors that need to be fixed. The latest update includes fixes for known ESLint errors, but if you encounter any new ones:

1. Check if the error is related to React hooks being used incorrectly (inside loops, conditions, or nested functions)
2. Move the hook declarations to the top level of your component
3. For toggle state management inside loops or map functions, use an object with keys instead of individual useState hooks

### Merge Conflicts

If you encounter merge conflicts during the update:

1. Open the conflicted files in your editor
2. Look for conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`)
3. Resolve the conflicts by editing the files
4. Save the files
5. Stage the resolved files with `git add <filename>`
6. Complete the merge with `git commit -m "Resolved merge conflicts"`

### Dependency Issues

If you encounter issues with dependencies:

1. Try removing and reinstalling the dependencies:

```bash
# For Python dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# For frontend dependencies
cd frontend
rm -rf node_modules
npm install
cd ..
```

### Database Migration

If the update includes database schema changes:

1. Backup your existing database files
2. Run any migration scripts provided with the update
3. Verify that your data is intact after the migration

## Latest Features and Fixes

The latest update includes:

1. **Baseline Compliance Selection**
   - Support for CIS benchmarks, STIG benchmarks, Microsoft Security benchmarks
   - Custom compliance benchmarks upload in CSV or PDF format

2. **Remediation Steps for Failed Checks**
   - Detailed remediation steps for all failed compliance checks in technical reports

3. **Report Selection and Preview**
   - Option to select between technical and executive reports
   - Preview functionality before downloading reports
   - Support for PDF and CSV formats

4. **Enhanced Dashboard**
   - Summary of application purpose
   - Widget showing previous 5 assessments with trending graph
   - Quick access to start new assessments
   - Status display for running assessments

5. **Bug Fixes**
   - Fixed ESLint error in AssessmentResults.js related to React hooks usage
   - Improved state management for remediation steps display

## Support

If you encounter any issues during the update process, please:

1. Check the GitHub repository issues page for known problems
2. Consult the documentation for troubleshooting tips
3. Submit a new issue on GitHub with details about your problem

---

For more information, visit the [project repository](https://github.com/manabouprj/ad-security-assessment).
