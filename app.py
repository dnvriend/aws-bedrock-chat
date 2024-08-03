from bedrock import get_llm_for_model_selection, calculate_token_cost
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.callbacks.streamlit.streamlit_callback_handler import StreamlitCallbackHandler
from prompt import prompt_template
from toolset import list_of_tools
from renderer import process_content
from langchain.callbacks import get_openai_callback
import os

AWS_BEDROCK_REGION=os.environ.get("AWS_BEDROCK_REGION", "us-east-1")

if 'selected_model' not in st.session_state:
    st.session_state.selected_model = "Sonnet 3.5"

if 'messages' not in st.session_state:
    st.session_state.messages = []

st.set_page_config(page_title="Bot", page_icon=":bot:", layout="wide")

# Sidebar
st.sidebar.title("Settings")

model_options = ["Sonnet 3.5", "Sonnet 3", "Haiku 3"]

# Model selection
selected_model = st.sidebar.selectbox(
    "Select LLM Model",
    model_options,
    model_options.index(st.session_state.selected_model)
)

if st.sidebar.button("Apply Model"):
    st.session_state.selected_model = selected_model
    st.rerun()

# Display history size
history_size = len(st.session_state.messages)
st.sidebar.metric("History Size", history_size)

temperature = st.sidebar.slider("temperature", 0.0, 1.0, 0.0, 0.1)
max_tokens = st.sidebar.slider("max_tokens", 100, 200000, 100000, 100)
memory_size = st.sidebar.slider("memory_size", 5, 100, 50, 1)

# Toggle for token usage display
show_token_usage = st.sidebar.toggle("Show Token Usage", value=False)

if 'memory' not in st.session_state:
    st.session_state.memory = ConversationBufferWindowMemory(return_messages=True, memory_key="chat_history", k=memory_size)

# Main content
st.title("AWS Bedrock Chat")

user_query = st.chat_input("Your message")

print(f"{temperature}/{max_tokens}")
# Select the appropriate model
llm = get_llm_for_model_selection(st.session_state.selected_model)

agent = create_tool_calling_agent(
    tools=list_of_tools,
    llm=llm,
    prompt=prompt_template(),
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=list_of_tools,
    memory=st.session_state.memory,
    verbose=True,
)

# Display conversation history
for message in st.session_state.messages:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)
    else:
        with st.chat_message("assistant"):
            process_content(message.content)

if user_query is not None and user_query != "":
    st.session_state.messages.append(HumanMessage(content=user_query))
    print(f'modelId: {llm.model_id}')
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            st_callback = StreamlitCallbackHandler(st.container(), expand_new_thoughts=True, collapse_completed_thoughts=True)
            config = {"callbacks": [st_callback]}

            with get_openai_callback() as cb:
                response = agent_executor.invoke({"input": user_query}, config=config)

                process_content(response['output'])

                if show_token_usage:
                    cost = calculate_token_cost(st.session_state.selected_model, cb.prompt_tokens, cb.completion_tokens)
                    st.write(f"Tokens: prompt:({cb.prompt_tokens}/{cost['input_cost']:.6f}), completion:({cb.completion_tokens}/{cost['output_cost']:.6f}), total:({cb.total_tokens}/{cost['total_cost']})")

    st.session_state.messages.append(AIMessage(content=response['output']))

    # Update memory with the new interaction
    st.session_state.memory.chat_memory.add_user_message(user_query)
    st.session_state.memory.chat_memory.add_ai_message(response['output'])