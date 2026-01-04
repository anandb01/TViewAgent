import streamlit as st
import requests
import time

API_BASE_URL = "http://localhost:8000"
REQUEST_TIMEOUT = 120

st.set_page_config(page_title="🤖 TViewAgent", layout="wide")
st.title("🤖 TViewAgent")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Show chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input("Ask about your documents..."):
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Show user message immediately
    with st.chat_message("user"):
        st.write(prompt)
    
    # Process response
    with st.chat_message("assistant"):
        status_container = st.empty()
        
        try:
            status_container.info("📤 Sending query...")
            response = requests.post(
                f"{API_BASE_URL}/chat",
                params={"qry": prompt},
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            job_data = response.json()
            job_id = job_data["job_id"]
            
            # Poll status
            start_time = time.time()
            max_wait = 180
            
            while time.time() - start_time < max_wait:
                status_response = requests.get(
                    f"{API_BASE_URL}/job_status",
                    params={"job_id": job_id},
                    timeout=10
                )
                status_response.raise_for_status()
                status_data = status_response.json()
                
                match status_data.get("status"):
                    case "queued":
                        status_container.info(f"⏳ **Queued** - Job: `{job_id}`")
                    case "running":
                        status_container.info("⚙️ **Processing**...")
                    case "completed":
                        result = status_data.get("result", "No response")
                        status_container.empty()
                        st.write(result)
                        st.session_state.messages.append({"role": "assistant", "content": result})
                        st.success(f"✅ Done! ({time.time()-start_time:.1f}s)")
                        break
                    case "failed":
                        error = status_data.get("error", "Unknown")
                        status_container.error(f"❌ **Failed**: {error}")
                        break
                    case _:
                        status_container.info("⏳ **Waiting**...")
                
                time.sleep(1)
            
            if time.time() - start_time > max_wait:
                status_container.error("⏰ **Timeout**")
                
        except Exception as e:
            status_container.error(f"💥 Error: {str(e)}")

# Clear chat
if st.button("🗑️ Clear Chat", use_container_width=True):
    st.session_state.messages = []
    st.rerun()
