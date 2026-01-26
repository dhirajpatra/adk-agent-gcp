#!/bin/bash
# Quick setup script for E-commerce Recommendation System
# Modular structure with separate files

echo "🚀 Setting up E-commerce Recommendation System..."

# Step 1: Install dependencies
pip install google-adk requests python-dotenv

# Step 2: Create .env file
cp ../env_copy .env

echo "⚠️  Remember to update .env with your GCP project ID"
