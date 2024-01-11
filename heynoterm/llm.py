from openai import OpenAI, AsyncOpenAI

client = OpenAI()
client = AsyncOpenAI()


# Initialize OpenAI client
async def stream_output(input_text):
    # Stream the output
    # use chatgpt 3.5 engine
    system_message = """
    Answer or complete the following text which is a part of a text in a document
    dont repeat the text in the document and continue the text
    """
    user_message = f"""text:
    ----
    {input_text}
    ----
                """
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=100,
        temperature=0.7,
        n=1,
        stop=None,
        stream=True,
    )

    async for item in response:
        yield item.choices[0].delta.content


if __name__ == "__main__":
    # Test cases
    input_text = "Once upon a time"
    for output in stream_output(input_text):
        print(output, end="", flush=True)

    input_text = "Hello, world!"
    outputs = list(stream_output(input_text))
    print(outputs)
