import os
import logging
import random
import sqlite3
from utils import get_db_connection, get_chroma_client, search_web, log_interaction
import google.generativeai as genai

logger = logging.getLogger("AIAgent")

def ensure_ai_ready():
    import streamlit as st
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.sidebar.warning("⚠️ Gemini API key not configured. Using fallback AI logic.")
        return False
    try:
        genai.configure(api_key=api_key)
        # Simple test request
        model = genai.GenerativeModel('models/gemini-1.5-pro-latest')
        response = model.generate_content("Hello")
        st.sidebar.success("🤖 Gemini AI Agent Ready")
        return True
    except Exception as e:
        st.sidebar.warning(f"Gemini AI setup failed: {str(e)}. Using fallback logic.")
        return False

def classify_issue_with_ai(description):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return classify_issue_fallback(description)
    
    try:
        genai.configure(api_key=api_key)
        prompt = f'''
Classify this maintenance issue into one of these categories: Plumbing, Electrical, HVAC, Structural, Appliance, Other.
Also determine the priority level: High, Medium, Low.

Issue description: {description}

Respond in format: Category: [category], Priority: [priority]
'''
        model = genai.GenerativeModel('models/gemini-1.5-pro-latest')
        response = model.generate_content(prompt)
        result = response.text.strip()
        
        # Parse response
        category, priority = "Other", "Medium"
        
        if "Category:" in result:
            parts = result.split("Category:")[1].split(",")
            if len(parts) > 0:
                cat_part = parts[0].strip()
                if cat_part in ["Plumbing", "Electrical", "HVAC", "Structural", "Appliance", "Other"]:
                    category = cat_part
        
        if "Priority:" in result:
            parts = result.split("Priority:")[1].split(",")
            if len(parts) > 0:
                pri_part = parts[0].strip()
                if pri_part in ["High", "Medium", "Low"]:
                    priority = pri_part
        
        return category, priority
    except Exception as e:
        logger.error(f"Gemini AI classification failed: {str(e)}")
        return classify_issue_fallback(description)

def classify_issue_fallback(description):
    keywords = {
        "Plumbing": ["water", "leak", "pipe", "drain", "faucet", "toilet", "sink", "plumbing", "shower", "bath"],
        "Electrical": ["light", "outlet", "power", "electrical", "wire", "switch", "electric", "bulb", "circuit"],
        "HVAC": ["air", "heating", "cooling", "temperature", "ac", "heat", "hvac", "thermostat", "fan", "vent"],
        "Structural": ["wall", "ceiling", "floor", "crack", "door", "window", "structural", "foundation", "roof"],
        "Appliance": ["refrigerator", "oven", "washer", "dryer", "dishwasher", "appliance", "microwave", "disposal"]
    }

    desc_lower = description.lower()
    scores = {cat: sum(1 for w in words if w in desc_lower) for cat, words in keywords.items()}
    category = max(scores, key=scores.get) if max(scores.values()) > 0 else "Other"

    urgent_keywords = ["urgent", "emergency", "broken", "not working", "leak", "no power", "no heat", "no cooling"]
    medium_keywords = ["intermittent", "sometimes", "occasionally", "slow"]

    if any(word in desc_lower for word in urgent_keywords):
        priority = "High"
    elif any(word in desc_lower for word in medium_keywords):
        priority = "Medium"
    else:
        priority = "Low"

    return category, priority

def classify_issue(description):
    return classify_issue_with_ai(description)

def estimate_cost_with_ai(description, category):
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return estimate_cost_fallback(category)

        # First try to get historical cost data from database
        try:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("SELECT estimated_cost FROM solutions_database WHERE issue_category=? ORDER BY estimated_cost", (category,))
            db_costs = [row[0] for row in c.fetchall()]
            conn.close()
            if db_costs:
                avg_cost = sum(db_costs)/len(db_costs)
                return round(avg_cost * random.uniform(0.8, 1.2), 2)
        except:
            pass

        # Use Gemini API for cost estimation
        genai.configure(api_key=api_key)
        prompt = f'''
Estimate the cost for this maintenance issue in USD. Consider labor and materials.
Category: {category}
Description: {description}
Provide only a number (no currency symbol).
'''
        model = genai.GenerativeModel('gemini-1.0-pro')
        response = model.generate_content(prompt)
        cost_str = response.text.strip()
        
        # Extract number
        try:
            # Remove all non-digit characters (except decimal point)
            cost_str_clean = ''.join(c for c in cost_str if c.isdigit() or c == '.')
            cost = float(cost_str_clean)
            # Ensure cost is within reasonable range
            return max(25.0, min(cost, 1000.0))
        except ValueError:
            return estimate_cost_fallback(category)
    except Exception as e:
        logger.error(f"Gemini AI cost estimation failed: {str(e)}")
        return estimate_cost_fallback(category)

def estimate_cost_fallback(category):
    base_costs = {"Plumbing":150,"Electrical":200,"HVAC":300,"Structural":400,"Appliance":250,"Other":100}
    base_cost = base_costs.get(category, 100)
    return round(base_cost*random.uniform(0.7,1.3),2)

def estimate_cost(description, category):
    return estimate_cost_with_ai(description, category)

def get_solutions_from_database(category, description, top_k=3):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute(
            "SELECT problem_description, solution_steps, estimated_cost, estimated_time, difficulty_level FROM solutions_database WHERE issue_category=? ORDER BY estimated_cost LIMIT ?",
            (category, top_k)
        )
        results = c.fetchall()
        if not results:
            c.execute(
                "SELECT problem_description, solution_steps, estimated_cost, estimated_time, difficulty_level FROM solutions_database LIMIT ?",
                (top_k,)
            )
            results = c.fetchall()
        conn.close()
        return [{"title":r[0],"snippet":r[1],"cost":r[2],"time":r[3],"difficulty":r[4]} for r in results]
    except Exception as e:
        logger.error(f"Database solution lookup failed: {str(e)}")
        return []

def recommend_solutions(description, category, top_k=3):
    solutions = get_solutions_from_database(category, description, top_k)
    try:
        collection = get_chroma_client()
        if collection.count()>0:
            results = collection.query(query_texts=[description], n_results=min(2,collection.count()))
            if results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    solutions.append({
                        "title": f"Knowledge Base Solution {i+1}",
                        "snippet": doc[:200]+"..." if len(doc)>200 else doc,
                        "difficulty": "Varies",
                        "cost":"Contact for estimate",
                        "time":"Varies"
                    })
    except Exception as e:
        logger.error(f"ChromaDB query failed: {str(e)}")
    try:
        web_results = search_web(f"{category} {description}")
        for result in web_results[:1]:
            solutions.append({
                "title": result["title"],
                "snippet": result["snippet"],
                "difficulty": "Varies",
                "cost":"See source",
                "time":"Varies"
            })
    except Exception as e:
        logger.error(f"Web search failed: {str(e)}")
    return solutions[:top_k]

def generate_ai_response(tenant_id, question, context=""):
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            try:
                genai.configure(api_key=api_key)
                prompt = f'''
You are a helpful maintenance assistant. Answer this question about maintenance issues.
Context: {context}
Question: {question}
Provide a helpful, practical answer.
'''
                model = genai.GenerativeModel('gemini-1.0-pro')
                response = model.generate_content(prompt)
                ai_response = response.text.strip()
            except Exception as e:
                logger.error(f"Gemini AI response generation failed: {str(e)}")
                ai_response = f"Thank you for your question about maintenance. Due to high demand, we're using our standard response system. Our team will review '{question}' and provide detailed assistance shortly."
        else:
            ai_response = f"Thank you for your question about {question}. Our maintenance team will review this and provide assistance."

        log_interaction(tenant_id, question, ai_response, "AI Response")
        return ai_response
    except Exception as e:
        logger.error(f"AI response generation failed: {str(e)}")
        fallback_response = f"Thank you for your question. We'll get back to you shortly."
        log_interaction(tenant_id, question, fallback_response, "Fallback Response")
        return fallback_response