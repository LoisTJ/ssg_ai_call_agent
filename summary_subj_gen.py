import openai
from ast import *
from config import *
from sample_case_transcript import sample_case_transcript
import json
from flask import Flask

app = Flask(__name__)

openai_api_key = OPENAI_API_KEY
openai_api_base_url = OPENAI_API_BASE_URL
openai_api_version = OPENAI_API_VERSION
openai_api_4o_model = OPENAI_API_4O_MODEL

# Function for GPT calls
def get_gpt4o_completion(sys_msg: list, model=openai_api_4o_model, temperature=0.1) -> str: # gpt-4-turbo
    client = openai.OpenAI(
        api_key=openai_api_key,
        base_url=openai_api_base_url,
        default_headers={"user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/81.0"},)
    response = client.chat.completions.create(
        model=model, 
        messages = sys_msg,
        response_format={"type": "json_object"},
        seed=6800,
        temperature=temperature
    )
    try:
        completion_output = literal_eval(response.choices[0].message.content)
        return completion_output
    except:
        completion_output = response.choices[0].message.content
        return completion_output

# Template for Case Summary generation prompt
def case_summary_gpt4o_sys_msg(case_transcript):
    sys_messages = [
        {
            "role": "system",
            "content": """
            You are a helpful assistant and an expert in Customer Relationship Management (CRM) case data. Help me to summarise each CRM case transcript into no more than 100 words. Be concise, but retain key systems, policy, programmes and all essential information in the case content related to the issue that is being reflected. Do not infer beyond the information given in the case descriptions. Give your response in JSON format as {"summary": "generated summary of the case transcript"}
            """
        },
        {
            "role": "user",
            "content": f"""
            "case_description": {case_transcript}.
            Summarise the case_description given into less than 100 words, give the output in JSON format.
            """
        }
    ]
    
    return sys_messages

# Template for Case Subject generation prompt
def case_subject_gpt4o_sys_msg(case_summary):
    sys_messages = [
        {
            "role": "system",
            "content": """
            You are a helpful assistant and an expert in Customer Relationship Management (CRM) case data. Help me to determine the subject of each CRM case summary into no more than 15 words. Be concise, and focus on the topic of the issue mentioned in the case summary. Retain only key systems, policy, programmes and all essential information in the case content related to the issue that is being reflected. Do not infer beyond the information given in the case descriptions. Give your response in JSON format as {"subject": "generated case subject of the case summary"}
            """
        },
        {
            "role": "user",
            "content": f"""
            "case_summary": {case_summary}.
            Summarise the case_summary given into less than 15 words, give the output in JSON format.
            """
        }
    ]
    
    return sys_messages

def main(case_transcript: str) -> tuple[dict[str], dict[str]]:
	"""
	This function generates the case summary and subject from the case transcript.
	:output:
		case_summary: str
		case_subject: str
	"""
	summary_prompt = case_summary_gpt4o_sys_msg(case_transcript)
	case_summary = get_gpt4o_completion(sys_msg=summary_prompt)
	subject_prompt = case_subject_gpt4o_sys_msg(case_summary)
	case_subject = get_gpt4o_completion(sys_msg=subject_prompt)
	
	return case_summary, case_subject

@app.route("/")
def test():
    return "HELLO FROM SSG!"

@app.route("/call")
def trigger(case_transcript):
    # case_transcript = sample_case_transcript
    output = main(case_transcript)
    print(output)
    return output

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)