import streamlit as st
import asyncio
import json
from datetime import datetime
import time
from agents import Runner
from MLagents.AIagents import professor_agent, storytelling_agent, argument_agent, case_study_agent

# Page configuration
st.set_page_config(
    page_title="ML Tutor Assistant", 
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .week-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    
    .topic-badge {
        background: #e3f2fd;
        color: #1565c0;
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        margin: 0.2rem;
        display: inline-block;
    }
    
    .skill-progress {
        background: #f0f0f0;
        border-radius: 10px;
        overflow: hidden;
        margin: 0.2rem 0;
    }
    
    .progress-bar {
        height: 20px;
        background: linear-gradient(90deg, #4CAF50, #45a049);
        text-align: center;
        line-height: 20px;
        color: white;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Load course data
@st.cache_data
def load_course_data():
    with open("MLplanningagent.json", "r") as f:
        return json.load(f)

course_data = load_course_data()
schedule = {w["WeekNumber"]: w for w in course_data["CourseSchedule"]["Schedule"]}
HARDCODED_DATE = datetime.strptime("2025-09-02", "%Y-%m-%d").date()

def get_week_by_date():
    today = HARDCODED_DATE
    for week in schedule.values():
        start = datetime.strptime(week["StartDate"], "%Y-%m-%d").date()
        end = datetime.strptime(week["EndDate"], "%Y-%m-%d").date()
        if start <= today <= end:
            return week
    return None

def get_agent_description(agent_type):
    descriptions = {
        "professor": "🎓 **Professor Mode**: Structured explanations with mathematical rigor",
        "storytelling": "📚 **Storytelling Mode**: Learn through engaging narratives", 
        "argument": "⚖️ **Debate Mode**: Explore different perspectives",
        "case_study": "🏢 **Case Study Mode**: Practical applications"
    }
    return descriptions.get(agent_type, "")

# Simple prompt handler function
async def handle_student_prompt(user_input: str, selected_week_data: dict, agent_type: str):
    """Simple prompt handler without progress tracking"""
    
    week_number = selected_week_data["WeekNumber"]
    topics = selected_week_data["Topics"]
    skills = selected_week_data.get("skills", {})
    readings = selected_week_data.get("readings", [])
    learning_objectives = selected_week_data.get("learningObjectives", [])
    
    # Create context for the selected agent
    context = f"""
Week {week_number} Context:
Topics: {', '.join(topics)}
Skills Focus: {', '.join(skills.keys())}
Readings: {'; '.join(readings) if readings else 'None'}
Learning Objectives: {'; '.join(learning_objectives) if learning_objectives else 'General understanding'}

Student Input: "{user_input}"
"""
    
    # Map and run agent
    agent_map = {
        "professor": professor_agent,
        "storytelling": storytelling_agent, 
        "argument": argument_agent,
        "case_study": case_study_agent
    }
    
    selected_agent = agent_map.get(agent_type, professor_agent)
    response = await Runner.run(selected_agent, context)
    
    return response.final_output

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Header
st.markdown("""
<div class="main-header">
    <h1>🤖 ML Tutor Assistant</h1>
    <p>Your AI companion for Machine Learning education</p>
</div>
""", unsafe_allow_html=True)

# Main layout
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 📅 Course Navigation")
    
    # Week selection
    week_numbers = list(schedule.keys())
    default_week = get_week_by_date()
    default_index = week_numbers.index(default_week["WeekNumber"]) if default_week else 0
    
    selected_week_num = st.selectbox(
        "Select Week", 
        week_numbers, 
        index=default_index,
        format_func=lambda x: f"Week {x}"
    )
    selected_week = schedule[selected_week_num]
    
    # Week info card
    st.markdown(f"""
    <div class="week-card">
        <h4>Week {selected_week['WeekNumber']}</h4>
        <p><strong>📆 Duration:</strong> {selected_week['StartDate']} → {selected_week['EndDate']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Topics
    st.markdown("#### 🧠 Topics This Week")
    for topic in selected_week.get("Topics", []):
        st.markdown(f'<span class="topic-badge">{topic}</span>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Skills with progress bars
    if selected_week.get("skills"):
        st.markdown("#### 📈 Skills Focus")
        for skill, weight in selected_week["skills"].items():
            st.markdown(f"""
            <div class="skill-progress">
                <div class="progress-bar" style="width: {weight}%">
                    {skill}: {weight:.0f}%
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Learning objectives
    if selected_week.get("learningObjectives"):
        st.markdown("#### 🎯 Learning Objectives")
        for objective in selected_week["learningObjectives"]:
            st.markdown(f"• {objective}")
    
    # Readings
    if selected_week.get("readings"):
        st.markdown("#### 📖 Required Readings")
        for reading in selected_week["readings"]:
            st.markdown(f"• {reading}")

with col2:
    # Agent selector
    st.markdown("### 🎯 Choose Your Learning Style")
    
    agent_type = st.radio(
        "Select how you'd like to learn:",
        ["professor", "storytelling", "argument", "case_study"],
        format_func=lambda x: {
            "professor": "🎓 Professor Mode", 
            "storytelling": "📚 Storytelling Mode",
            "argument": "⚖️ Argument Mode",
            "case_study": "🏢 Case Study Mode"
        }[x],
        horizontal=True
    )
    
    # Display agent description
    st.markdown(get_agent_description(agent_type))
    
    # Chat interface
    st.markdown("### 💬 Chat with Your ML Tutor")
    
    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if "timestamp" in msg:
                st.caption(f"⏰ {msg['timestamp']}")
    
    # Chat input
    prompt = st.chat_input("💭 Ask me anything about this week's ML topics...")
    
    if prompt:
        # Add user message
        st.session_state.messages.append({
            "role": "user", 
            "content": prompt,
            "timestamp": datetime.now().strftime("%H:%M")
        })
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
            st.caption(f"⏰ {datetime.now().strftime('%H:%M')}")
        
        # Generate response
        with st.spinner("🤔 Let me think about that..."):
            response = asyncio.run(
                handle_student_prompt(prompt, selected_week, agent_type)
            )
            
            # Display assistant response with typing effect
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                displayed_response = ""
                for char in response:
                    displayed_response += char
                    response_placeholder.write(displayed_response)
                    time.sleep(0.01)
                
                st.caption(f"⏰ {datetime.now().strftime('%H:%M')}")
            
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response,
                "timestamp": datetime.now().strftime("%H:%M")
            })
        
        st.rerun()
    
    # Chat management
    if st.session_state.messages:
        col_clear, col_export = st.columns(2)
        
        with col_clear:
            if st.button("🗑️ Clear Chat", type="secondary"):
                st.session_state.messages = []
                st.rerun()
        
        with col_export:
            if st.button("💾 Export Chat", type="secondary"):
                chat_export = {
                    "week": selected_week_num,
                    "agent_type": agent_type,
                    "timestamp": datetime.now().isoformat(),
                    "messages": st.session_state.messages
                }
                st.download_button(
                    label="📥 Download Chat",
                    data=json.dumps(chat_export, indent=2),
                    file_name=f"ml_chat_week_{selected_week_num}_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                    mime="application/json"
                )