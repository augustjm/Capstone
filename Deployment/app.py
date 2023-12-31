import streamlit as st
from llama_index import VectorStoreIndex, ServiceContext, Document
from llama_index.llms import OpenAI
import openai
from llama_index import StorageContext, load_index_from_storage


st.set_page_config(page_title="Chat with TripAdvisor Bar Reviews", page_icon="🥤", layout="centered", initial_sidebar_state="auto", menu_items=None)
openai.api_key = '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'#st.secrets.openai_key
st.markdown("<h1 style='text-align: center;'>Chat with TripAdvisor Bar Reviews ☕️🧃🥤</h1>", unsafe_allow_html=True)
st.caption("powered by LlamaIndex and finetuned GPT3.5turbo")

if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask me a question about Singapore Bars"}
    ]

@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading and indexing the TripAdvisor docs – hang tight! This should take 1-2 minutes."):
        
        # Rebuild the storage context
        storage_context = StorageContext.from_defaults(persist_dir="./data/index.vecstore")

        # Load the index
        index = load_index_from_storage(storage_context)

        # Load the finetuned model 
        ft_model_name = "ft:gpt-3.5-turbo-0613:personal::80aOEYbP"
        ft_context = ServiceContext.from_defaults(llm=OpenAI(model=ft_model_name, temperature=0.2), context_window=2048, system_prompt="You are an expert on the TripAdvisor attraction review documents and ratings and your job is to answer questions related to the reviews. Assume that all questions are related to the TripAdvisor attraction review. Keep your answers technical and based on facts – do not hallucinate features.")
        return index

index = load_data()
chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)

if prompt := st.chat_input("Your question"): # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages: # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = chat_engine.chat(prompt)
            st.write(response.response)
            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message) # Add response to message history