from langchain_aws import ChatBedrock
import boto3

def _get_bedrock_model(model_id: str, temperature: int, max_tokens: int, region: str) -> ChatBedrock:
    bedrock_client = boto3.client('bedrock-runtime', region)
    return ChatBedrock(model_id=model_id,
                       client=bedrock_client,
                       model_kwargs={"temperature": temperature, "max_tokens": max_tokens},
                       streaming=False,
    )

def get_sonnet_3(max_tokens: int, temperature: int, region: str) -> ChatBedrock:
    model_id="anthropic.claude-3-sonnet-20240229-v1:0"
    return _get_bedrock_model(model_id, temperature, max_tokens, region)

def get_sonnet_35(max_tokens: int, temperature: int, region: str) -> ChatBedrock:
    model_id="anthropic.claude-3-5-sonnet-20240620-v1:0"
    return _get_bedrock_model(model_id, temperature, max_tokens, region)

def get_haiku_3(max_tokens: int, temperature: int, region: str) -> ChatBedrock:
    model_id="anthropic.claude-3-haiku-20240307-v1:0"
    return _get_bedrock_model(model_id, temperature, max_tokens, region)

def get_llm_for_model_selection(model_selection: str) -> ChatBedrock:
    if model_selection == "Sonnet 3":
        return get_sonnet_3(max_tokens=100000, temperature=0, region="us-east-1")
    elif model_selection == "Sonnet 3.5":
        return get_sonnet_35(max_tokens=100000, temperature=0, region="us-east-1")
    elif model_selection == "Haiku 3":
        return get_haiku_3(max_tokens=100000, temperature=0, region="us-east-1")
    else:
        raise ValueError("Unknown model")

def calculate_token_cost(model: str, input_tokens: int, output_tokens: int) -> dict:
    if model in ["Sonnet 3", "Sonnet 3.5"]:
        input_cost = (input_tokens / 1000) * 0.003
        output_cost = (output_tokens / 1000) * 0.015
    elif model == "Haiku 3":
        input_cost = (input_tokens / 1000) * 0.00025
        output_cost = (output_tokens / 1000) * 0.00125
    else:
        raise ValueError("Unknown model")

    total_cost = input_cost + output_cost
    return {
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": total_cost
    }