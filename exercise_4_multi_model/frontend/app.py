
import streamlit as st
import requests
from typing import List, Dict
import time

API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="Multi-Model Chat",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_provider" not in st.session_state:
    st.session_state.selected_provider = "ollama"

# Helper Functions

def get_providers() -> List[Dict]:
    try:
        response = requests.get(f"{API_BASE_URL}/providers", timeout=5)
        if response.status_code == 200:
            return response.json()["providers"]
        else:
            st.error(f"Failed to fetch providers: {response.status_code}")
            return []
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to API. Make sure the FastAPI server is running!")
        return []
    except Exception as e:
        st.error(f"Error fetching providers: {str(e)}")
        return []

def send_message(provider: str, prompt: str, model_name: str = None, temperature: float = 0.7) -> Dict:
    try:
        payload = {
            "provider": provider,
            "prompt": prompt,
            "temperature": temperature
        }
        
        if model_name:
            payload["model_name"] = model_name
        
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"API error: {response.status_code}",
                "response": ""
            }
    
    except requests.exceptions.Timeout:
        return {
            "error": "Request timed out. The model might be too slow or unavailable.",
            "response": ""
        }
    except Exception as e:
        return {
            "error": f"Error: {str(e)}",
            "response": ""
        }

# UI Layout

st.title("🤖 Multi-Model Chat")
st.markdown("Chat with different LLM providers: **Groq**, **HuggingFace**, and **Ollama**")

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Fetch providers
    providers = get_providers()
    
    if providers:
        st.subheader("Available Providers")
        
        # Display provider status
        for provider in providers:
            name = provider["name"].title()
            available = provider["available"]
            
            if available:
                st.success(f"✅ {name}")
            else:
                st.warning(f"⚠️ {name} (Not configured)")
        
        st.divider()
        
        # Provider selection
        available_providers = [p["name"] for p in providers if p["available"]]
        
        if available_providers:
            selected_provider = st.selectbox(
                "Select Provider",
                available_providers,
                index=available_providers.index(st.session_state.selected_provider) 
                      if st.session_state.selected_provider in available_providers 
                      else 0,
                key="provider_select"
            )
            st.session_state.selected_provider = selected_provider
            
            # Model selection (for providers that support it)
            current_provider_info = next(
                (p for p in providers if p["name"] == selected_provider), 
                None
            )
            
            if current_provider_info:
                provider_details = current_provider_info["info"]
                
                # Show current model
                st.info(f"**Current Model:** {provider_details.get('model', 'N/A')}")
                
                # For Ollama, show installed models
                if selected_provider == "ollama" and "installed_models" in provider_details:
                    installed = provider_details["installed_models"]
                    if installed:
                        st.success(f"**Installed Models:** {', '.join(installed)}")
                    else:
                        st.warning("No models installed. Run `ollama pull <model>` to install.")
                
                # Custom model name input
                custom_model = st.text_input(
                    "Custom Model Name (optional)",
                    placeholder="Leave empty for default"
                )
            
            # Temperature slider
            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                step=0.1,
                help="Higher values make output more random, lower values more deterministic"
            )
            
            st.divider()
            
            # Clear chat button
            if st.button("🗑️ Clear Chat History"):
                st.session_state.messages = []
                st.rerun()
        
        else:
            st.error("No providers are configured!")
            st.markdown("""
            **To get started:**
            1. Make sure FastAPI server is running
            2. Configure at least one provider:
               - **Ollama**: Run `ollama serve`
               - **Groq**: Add API key to `.env`
               - **HuggingFace**: Add token to `.env`
            """)
    
    else:
        st.error("Cannot connect to API server")
        st.markdown("""
        **Start the API server:**
        ```bash
        cd backend
        python main.py
        ```
        """)

# Main chat area
st.divider()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Show provider info for assistant messages
        if message["role"] == "assistant" and "provider" in message:
            st.caption(f"*via {message['provider'].title()} ({message.get('model', 'unknown')})*")

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Check if any provider is available
    if not providers or not any(p["available"] for p in providers):
        st.error("No providers available. Please configure at least one provider.")
    else:
        # Add user message to chat
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner(f"Thinking with {st.session_state.selected_provider.title()}..."):
                # Get custom model name if provided
                model_override = custom_model if custom_model else None
                
                # Send request
                response = send_message(
                    st.session_state.selected_provider,
                    prompt,
                    model_name=model_override,
                    temperature=temperature
                )
                
                # Display response
                if response.get("error"):
                    st.error(f"Error: {response['error']}")
                    assistant_message = f"Error: {response['error']}"
                else:
                    st.markdown(response["response"])
                    st.caption(f"*via {response['provider'].title()} ({response['model']})*")
                    assistant_message = response["response"]
                
                # Add assistant message to chat
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_message,
                    "provider": st.session_state.selected_provider,
                    "model": response.get("model", "unknown")
                })

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.8em;'>
    Multi-Model Chat Application | Built with FastAPI & Streamlit
</div>
""", unsafe_allow_html=True)
