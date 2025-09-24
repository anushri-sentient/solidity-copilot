import streamlit as st
import requests
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import logging
from prompts import get_solidity_expert_prompt, get_assumptions_prompt, parse_assumptions_response
import urllib3
import certifi
import ssl

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('solidity_copilot.log')
    ]
)
logger = logging.getLogger(__name__)

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="Solidity Copilot",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
# Load custom CSS from an external file
css_file_path = os.path.join(os.path.dirname(__file__), "styles.css")
if os.path.exists(css_file_path):
    with open(css_file_path, "r") as css_file:
        st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)
else:
    logger.warning("Custom CSS file 'styles.css' not found. UI may not be styled as intended.")

class SolidityCopilot:
    def __init__(self):
        logger.info("🚀 Initializing SolidityCopilot...")
        
        self.api_key = os.getenv("FIREWORKS_API_KEY")
        self.base_url = os.getenv("FIREWORKS_BASE_URL", "https://api.fireworks.ai/inference/v1")
        self.model_name = os.getenv("_FIREWORKS_DEDICATED_GPT_OSS_120B_MODEL_NAME", 
                                  "accounts/sentientfoundation/loadBalancers/gpt-oss-120b")
        
        logger.info(f"📡 API Configuration:")
        logger.info(f"   - Base URL: {self.base_url}")
        logger.info(f"   - Model: {self.model_name}")
        logger.info(f"   - API Key: {'✅ Set' if self.api_key else '❌ Missing'}")
        
        if not self.api_key:
            logger.error("❌ API key not found in environment variables")
            st.error("⚠️ Please set your Firework API key in the .env file")
            st.stop()
        
        # Debug: Show the actual URL being used
        logger.info("✅ SolidityCopilot initialized successfully")
    

    def display_flow_visualization(self, user_input, primary_response, improved_response):
        """Display beautiful flow visualization of the three-call architecture"""
        
        st.markdown("---")
        st.markdown("## 🔄 **Three-Call Architecture Flow Visualization**")
        
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; margin: 20px 0;">
            <h3 style="color: white; text-align: center; margin: 0;">✨ Advanced AI Architecture Flow</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Step 1: Primary Generation
        with st.expander("🎯 **Step 1: Primary Response Generation**", expanded=True):
            st.markdown("""
            <div style="background: #e3f2fd; padding: 15px; border-radius: 10px; border-left: 5px solid #2196f3; margin-bottom: 15px;">
                <h4 style="margin: 0; color: #1976d2;">🤖 Primary AI</h4>
                <p style="margin: 5px 0; color: #424242;">Generates initial Solidity response</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("**📝 Input:**")
            st.code(user_input, language="text")
            
            st.markdown("**📤 Output:**")
            # Create scrollable container for long content
            st.markdown("""
            <div style="max-height: 400px; overflow-y: auto; border: 1px solid #e0e0e0; border-radius: 5px; padding: 10px; background: #f8f9fa;">
            """, unsafe_allow_html=True)
            st.code(primary_response, language="solidity")
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Step 2: Comprehensive Improvement
        with st.expander("✨ **Step 2: Senior Developer Review**", expanded=True):
            st.markdown("""
            <div style="background: #f3e5f5; padding: 15px; border-radius: 10px; border-left: 5px solid #9c27b0; margin-bottom: 15px;">
                <h4 style="margin: 0; color: #7b1fa2;">🔧 Senior Developer Review</h4>
                <p style="margin: 5px 0; color: #424242;">Expert review & enhancement for security, gas optimization, and best practices</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("**📤 Improved Code:**")
            # Create scrollable container for long content
            st.markdown("""
            <div style="max-height: 400px; overflow-y: auto; border: 1px solid #e0e0e0; border-radius: 5px; padding: 10px; background: #f8f9fa;">
            """, unsafe_allow_html=True)
            st.code(improved_response, language="solidity")
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Step 3: Assumptions Analysis
        with st.expander("🔍 **Step 3: Assumptions Analysis**", expanded=True):
            st.markdown("""
            <div style="background: #fff3e0; padding: 15px; border-radius: 10px; border-left: 5px solid #ff9800; margin-bottom: 15px;">
                <h4 style="margin: 0; color: #f57c00;">🔍 Assumptions AI</h4>
                <p style="margin: 5px 0; color: #424242;">Analyzes what assumptions were made</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("**📋 Assumptions Identified:**")
            st.markdown("""
            <div style="max-height: 200px; overflow-y: auto; border: 1px solid #e0e0e0; border-radius: 5px; padding: 10px; background: #f8f9fa;">
            """, unsafe_allow_html=True)
            st.markdown("Technical and security assumptions extracted from the final code")
            st.markdown("</div>", unsafe_allow_html=True)
                
        
        # Flow Summary
        st.markdown("""
        <div style="background: linear-gradient(135deg, #4caf50 0%, #45a049 100%); padding: 20px; border-radius: 15px; margin: 20px 0;">
            <h3 style="color: white; text-align: center; margin: 0;">🎯 **Process Complete**</h3>
            <p style="color: white; text-align: center; margin: 10px 0;">Three-call architecture: Generate → Improve → Analyze Assumptions</p>
        </div>
        """, unsafe_allow_html=True)
    
    def make_api_call(self, system_prompt, user_prompt, timeout=30):
        """Make a single API call with SSL handling"""
        logger.info(f"🌐 Making API call to {self.base_url}")
        logger.info(f"📝 User prompt length: {len(user_prompt)} characters")
        logger.info(f"🔧 System prompt length: {len(system_prompt)} characters")
        logger.info(f"⏱️ Timeout: {timeout} seconds")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "SolidityCopilot/1.0"
        }
        
        data = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 6000,
            "stream": False
        }
        
        logger.info(f"📊 Request data: model={self.model_name}, temperature=0.7, max_tokens=6000")
        
        # Simple API call with SSL handling
        try:
            logger.info("🔄 Attempting API call...")
            import requests
            import urllib3
            import ssl
            
            # Disable SSL warnings
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            # Create session with SSL context
            session = requests.Session()
            
            # Configure SSL context to handle hostname issues
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            ssl_context.set_ciphers('DEFAULT@SECLEVEL=0')
            
            # Set up session with SSL bypass
            session.verify = False
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Connection': 'keep-alive'
            })
            
            # Construct the full endpoint URL
            endpoint_url = f"{self.base_url}/chat/completions"
            logger.info(f"🌐 Making API call to {endpoint_url}")
            
            response = session.post(
                endpoint_url,
                headers=headers,
                json=data,
                timeout=timeout,
                verify=False
            )
            logger.info(f"✅ API call successful: {response.status_code}")
                
        except Exception as api_error:
            logger.error(f"❌ API call failed: {str(api_error)}")
            raise Exception(f"API call failed: {str(api_error)}")
        
        # Handle response
        if response.status_code == 200:
            response_data = response.json()
            content = response_data["choices"][0]["message"]["content"]
            logger.info(f"✅ API call successful - Response length: {len(content)} characters")
            logger.debug(f"📄 Response preview: {content[:200]}...")
            return content
        else:
            logger.error(f"❌ API Error: {response.status_code} - {response.text}")
            raise Exception(f"API Error: {response.status_code} - {response.text}")

    def get_response(self, user_input, use_two_call=False, use_three_call=False):
        """Get response from Firework API with optional two-call or simplified two-call architecture"""
        logger.info(f"🚀 Starting response generation for user input: {user_input[:100]}...")
        logger.info(f"🔧 Configuration: two_call={use_two_call}, three_call={use_three_call}")
        
        try:
            system_prompt = get_solidity_expert_prompt()
            logger.info("📝 Using expert prompt")
            
            if not use_two_call and not use_three_call:
                # Single call - original behavior
                logger.info("⚡ Single call mode - generating response")
                return self.make_api_call(system_prompt, user_input)
            elif use_three_call:
                # Simplified Two-Call Architecture: Primary Generation + Improvement
                logger.info("✨ Two-call architecture activated")
                
                # Primary call - generate main response
                logger.info("🎯 Step 1: Generating primary response")
                with st.spinner("🤖 Generating primary response..."):
                    primary_response = self.make_api_call(system_prompt, user_input)
                logger.info(f"✅ Primary response generated - Length: {len(primary_response)} characters")
                
                # Second call - comprehensive improvement
                logger.info("✨ Step 2: Improving response with comprehensive review")
                with st.spinner("✨ Improving response with comprehensive review..."):
                    # Create a comprehensive improvement prompt that combines technical and security review
                    improvement_prompt = f"""Please review and improve the following Solidity code. Focus on:

1. **Technical Accuracy**: Ensure the code is correct, complete, and follows best practices
2. **Security**: Identify and fix any security vulnerabilities
3. **Gas Optimization**: Optimize for gas efficiency where possible
4. **Code Quality**: Improve readability, documentation, and structure

Original Request: {user_input}

Generated Code:
{primary_response}

Please provide an improved version of the code that addresses any issues you find. If the code is already excellent, provide it with minor improvements or additional comments."""
                    
                    improved_response = self.make_api_call(
                        "You are a senior Solidity expert specializing in security, gas optimization, and best practices.", 
                        improvement_prompt,
                        timeout=45  # Increased timeout for the improvement call
                    )
                logger.info(f"✅ Improved response generated - Length: {len(improved_response)} characters")
                
                # Extract assumptions from the improvement process
                logger.info("🔍 Extracting assumptions from improvement process")
                
                try:
                    assumptions_prompt = get_assumptions_prompt(user_input, improved_response)
                    assumptions_response = self.make_api_call(
                        "You are a Solidity code analyst who identifies assumptions and design decisions in smart contract code.",
                        assumptions_prompt,
                        timeout=30
                    )
                    logger.info(f"✅ Assumptions extracted - Length: {len(assumptions_response)} characters")
                    
                    # Parse assumptions into categories
                    technical_assumptions, security_assumptions = parse_assumptions_response(assumptions_response)
                    
                except Exception as e:
                    logger.error(f"❌ Error extracting assumptions: {str(e)}")
                    technical_assumptions = "Error extracting technical assumptions from code analysis"
                    security_assumptions = "Error extracting security assumptions from code analysis"
            
                
                # Show improvement details in expanders
                with st.expander("✨ Comprehensive Improvement", expanded=False):
                    st.markdown("**Improvement Assessment:**")
                    st.text_area("Improvement Feedback", improved_response, height=200, disabled=True)
                
                # Show extracted assumptions in table format
                with st.expander("🔍 Extracted Assumptions", expanded=False):
                    # Parse assumptions into lists for table display
                    tech_list = technical_assumptions.split('\n') if technical_assumptions else []
                    sec_list = security_assumptions.split('\n') if security_assumptions else []
                    
                    # Create assumptions table
                    st.markdown("### 📋 **All Assumptions Made in Final Code**")
                    
                    # Technical Assumptions Table
                    if tech_list and any(item.strip() for item in tech_list):
                        st.markdown("#### 🔧 **Technical Assumptions**")
                        tech_data = []
                        for i, assumption in enumerate(tech_list, 1):
                            if assumption.strip():
                                tech_data.append({
                                    "ID": i,
                                    "Assumption": assumption.strip()
                                })
                        
                        if tech_data:
                            st.table(tech_data)
                    
                    # Security Assumptions Table
                    if sec_list and any(item.strip() for item in sec_list):
                        st.markdown("#### 🛡️ **Security Assumptions**")
                        sec_data = []
                        for i, assumption in enumerate(sec_list, 1):
                            if assumption.strip():
                                sec_data.append({
                                    "ID": i,
                                    "Assumption": assumption.strip()
                                })
                        
                        if sec_data:
                            st.table(sec_data)
                    
                    # Show message if no assumptions found
                    if not tech_list and not sec_list:
                        st.info("No specific assumptions identified in the generated code.")
                
                # Compile comprehensive assumptions
                all_assumptions = f"""
## 📋 **All Assumptions Made in Final Code**

### 🔧 **Technical Assumptions in Code**
{technical_assumptions}

### 🛡️ **Security Assumptions in Code**
{security_assumptions} """

                # Display beautiful flow visualization if enabled
                if st.session_state.show_flow_visualization:
                    logger.info("🎨 Displaying two-call architecture flow")
                    self.display_flow_visualization(
                        user_input, 
                        primary_response, 
                        improved_response
                    )
                else:
                    logger.info("⚡ Flow visualization disabled - showing compact view")

                # Return improved response with all assumptions
                return f"{improved_response}\n\n{all_assumptions}\n\n---\n*Two-Call Architecture Complete* - This response has been improved with comprehensive review covering technical accuracy, security, gas optimization, and best practices. All assumptions made in the final code that weren't explicitly specified by the user are documented above."
                
            else:
                # Fallback to single call if neither two-call nor three-call is enabled
                logger.info("⚡ Single call mode - generating response")
                return self.make_api_call(system_prompt, user_input)
                
        except Exception as e:
            logger.error(f"❌ Error in get_response: {str(e)}")
            st.error(f"Error: {str(e)}")
            return "Sorry, I encountered an error. Please try again."
    
    def _detect_multiple_files(self, response_text: str) -> bool:
        """Detect if the response contains multiple Solidity files or contracts"""
        # Look for indicators of multiple files/contracts
        indicators = [
            "contract " in response_text.lower(),
            "pragma solidity" in response_text.lower(),
            "// file:" in response_text.lower(),
            "// contract:" in response_text.lower(),
            "interface " in response_text.lower(),
            "library " in response_text.lower()
        ]
        
        # Count contract definitions
        contract_count = response_text.lower().count("contract ")
        interface_count = response_text.lower().count("interface ")
        library_count = response_text.lower().count("library ")
        
        total_definitions = contract_count + interface_count + library_count
        
        # Consider it multiple files if there are multiple definitions or specific indicators
        return total_definitions > 1 or any(indicators)
    
    def _extract_project_name(self, response_text: str) -> str:
        """Extract project name from the response text"""
        import re
        
        # Look for contract names
        contract_matches = re.findall(r'contract\s+(\w+)', response_text)
        if contract_matches:
            return contract_matches[0]
        
        # Look for project name patterns
        project_matches = re.findall(r'project[:\s]+(\w+)', response_text, re.IGNORECASE)
        if project_matches:
            return project_matches[0]
        
        # Default fallback
        return "SolidityProject"

def initialize_session_state():
    """Initialize session state variables"""
    logger.info("🔧 Initializing session state variables")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        logger.info("📝 Initialized messages list")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        logger.info("📚 Initialized chat history")
    # Expert mode is always active
    logger.info("🧠 Expert mode is always active")
    if "use_two_call" not in st.session_state:
        st.session_state.use_two_call = False
    if "use_three_call" not in st.session_state:
        st.session_state.use_three_call = True  # Default to simplified two-call architecture
        logger.info("✨ Set simplified two-call architecture as default")
    if "verification_details" not in st.session_state:
        st.session_state.verification_details = []
        logger.info("🔍 Initialized verification details")
    if "show_flow_visualization" not in st.session_state:
        st.session_state.show_flow_visualization = True  # Default to showing flow
        logger.info("🎨 Set flow visualization as default")
    
    logger.info("✅ Session state initialization complete")

def display_chat_message(role, content):
    """Display a chat message with proper styling"""
    if role == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>You:</strong><br>
            {content}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message assistant-message">
            <strong>Solidity Copilot:</strong><br>
            {content}
        </div>
        """, unsafe_allow_html=True)

def main():
    logger.info("🚀 Starting Solidity Copilot application")
    
    # Initialize session state
    logger.info("🔧 Initializing session state")
    initialize_session_state()
    
    # Initialize copilot
    logger.info("🤖 Initializing SolidityCopilot")
    copilot = SolidityCopilot()
    
    # Header - Simplified
    st.markdown('<h1 class="main-header">🔗 Solidity Copilot</h1>', unsafe_allow_html=True)
    st.markdown("**AI-Powered Smart Contract Development**")
    
    # Sidebar
    with st.sidebar:
       
        st.markdown("### ✨ Advanced AI Architecture")
        
        # Three-call is now the default and only mode
        st.session_state.use_two_call = False
        st.session_state.use_three_call = True
        
        
        # Clear chat button
        if st.button("🗑️ Clear Chat", type="secondary"):
            st.session_state.messages = []
            st.session_state.chat_history = []
            st.session_state.verification_details = []
            st.rerun()
        
        # Flow Visualization - Always Enabled
        st.markdown("### 🎨 Flow Visualization")
        st.session_state.show_flow_visualization = True  # Always enabled
        
        # How it works section
        st.markdown("### 🔄 How It Works")
        st.markdown("""
        **Three-Call Architecture:**
        1. **Primary Call**: Generates the main response
        2. **Senior Developer Review**: Reviews and improves technical accuracy, security, gas optimization, and best practices
        3. **Assumptions Analysis**: Analyzes what assumptions were made in the final code
        """)
        
        st.markdown("---")
    
    # Main chat interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 💬 Chat")
        
        # Default question buttons
        st.markdown("#### 🚀 Quick Start - Common Contract Types")
        
        # Create two rows of buttons
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            if st.button("📋 Registry Contract", help="Create a Registry Style contract for managing Artifacts"):
                prompt = "Create a Registry Style contract for managing Artifacts"
                st.session_state.messages.append({"role": "user", "content": prompt})
                display_chat_message("user", prompt)
                with st.spinner("🤔 Thinking..."):
                    response = copilot.get_response(prompt, st.session_state.use_two_call, st.session_state.use_three_call)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    display_chat_message("assistant", response)
                st.rerun()
            
            if st.button("🏦 Vault Contract", help="Create a Vault Contract"):
                prompt = "Create a Vault Contract"
                st.session_state.messages.append({"role": "user", "content": prompt})
                display_chat_message("user", prompt)
                with st.spinner("🤔 Thinking..."):
                    response = copilot.get_response(prompt, st.session_state.use_two_call, st.session_state.use_three_call)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    display_chat_message("assistant", response)
                st.rerun()
        
        with col_btn2:
            if st.button("💰 Staking Contract", help="Create a Staking Contract with yield"):
                prompt = "Create a Staking Contract with yield"
                st.session_state.messages.append({"role": "user", "content": prompt})
                display_chat_message("user", prompt)
                with st.spinner("🤔 Thinking..."):
                    response = copilot.get_response(prompt, st.session_state.use_two_call, st.session_state.use_three_call)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    display_chat_message("assistant", response)
                st.rerun()
            
            if st.button("🏪 Marketplace", help="Create a Marketplace Contract for trading NFTs/tokens"):
                prompt = "Create a Marketplace Contract to allow buying, selling, and trading of in-game assets (NFTs or tokens)"
                st.session_state.messages.append({"role": "user", "content": prompt})
                display_chat_message("user", prompt)
                with st.spinner("🤔 Thinking..."):
                    response = copilot.get_response(prompt, st.session_state.use_two_call, st.session_state.use_three_call)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    display_chat_message("assistant", response)
                st.rerun()
        
        with col_btn3:
            if st.button("🔒 Escrow Contract", help="Create an Escrow/Prize Pool Contract"):
                prompt = "Create a Escrow / Prize Pool Contracts to hold funds for tournaments, wagers, or bets until game outcomes are verified"
                st.session_state.messages.append({"role": "user", "content": prompt})
                display_chat_message("user", prompt)
                with st.spinner("🤔 Thinking..."):
                    response = copilot.get_response(prompt, st.session_state.use_two_call, st.session_state.use_three_call)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    display_chat_message("assistant", response)
                st.rerun()
            
            if st.button("🎁 Rewards Contract", help="Create a Reward Distribution Contract"):
                prompt = "Create Reward Distribution Contracts for play-to-earn reward payouts"
                st.session_state.messages.append({"role": "user", "content": prompt})
                display_chat_message("user", prompt)
                with st.spinner("🤔 Thinking..."):
                    response = copilot.get_response(prompt, st.session_state.use_two_call, st.session_state.use_three_call)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    display_chat_message("assistant", response)
                st.rerun()
        
        st.markdown("---")
        
        # Expert mode is always active
        
        # Display chat history
        for message in st.session_state.messages:
            display_chat_message(message["role"], message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask me anything about Solidity development..."):
            logger.info(f"💬 User input received: {prompt[:100]}...")
            
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": prompt})
            display_chat_message("user", prompt)
            logger.info("📝 User message added to chat history")
            
            # Get and display assistant response
            logger.info("🤔 Processing user request...")
            with st.spinner("🤔 Thinking..."):
                response = copilot.get_response(
                    prompt, 
                    st.session_state.use_two_call,
                    st.session_state.use_three_call
                )
                st.session_state.messages.append({"role": "assistant", "content": response})
                display_chat_message("assistant", response)
                logger.info(f"✅ Response generated and displayed - Length: {len(response)} characters")
    
    with col2:
        st.markdown("### 📊 Session Info")
        st.metric("Messages", len(st.session_state.messages))
        st.metric("Mode", "Expert")
        
        
        if st.session_state.messages:
            st.markdown("### 📝 Recent Topics")
            topics = []
            for msg in st.session_state.messages[-5:]:
                if msg["role"] == "user":
                    topics.append(msg["content"][:50] + "..." if len(msg["content"]) > 50 else msg["content"])
            
            for topic in topics:
                st.markdown(f"• {topic}")

if __name__ == "__main__":
    main()