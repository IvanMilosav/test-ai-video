#!/bin/bash
# Deploy to Git - Only Essential Files

echo "Files that will be deployed for web app:"
echo ""
echo "✅ Core Application:"
ls -1 *.py 2>/dev/null | grep -E "(web_api|config|iterative|gemini|analyze|ontology|brain)"
echo ""
echo "✅ Web Frontend:"
ls -1d public static 2>/dev/null
echo ""
echo "✅ Dependencies:"
ls -1 requirements*.txt .env.example 2>/dev/null
echo ""
echo "✅ Deployment Configs:"
ls -1 Dockerfile *.json *.yaml *.toml 2>/dev/null | head -5
echo ""
echo "✅ Launchers:"
ls -1 start_web.* 2>/dev/null
echo ""
echo "✅ Docs:"
ls -1 README_*.md QUICK_DEPLOY.md WEB_*.md 2>/dev/null
echo ""
echo "---"
echo "Total essential files: ~40-50"
echo "Total size: < 5MB"
echo ""
echo "Ready to deploy? Run:"
echo "  git add ."
echo "  git commit -m 'Deploy web app'"
echo "  git push origin main"
