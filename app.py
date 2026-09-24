import requests

url = "http://localhost:11434/api/generate"

system_prompt = """
Wewe ni msaidizi wa AI anayezungumza Kiswahili.
Jibu kwa Kiswahili rahisi, cha kawaida na kinachoeleweka.
Kuwa mwenye heshima, msaada na sahihi.
Ikiwa mtumiaji anauliza swali gumu, eleza hatua kwa hatua.
Usibadilishe lugha isipokuwa mtumiaji akuombe.
"""

conversation = []

while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        print("Kwaheri!")
        break

    conversation.append("Mtumiaji: " + user_input)

    prompt = system_prompt + "\n\n" + "\n".join(conversation)

    data = {
        "model": "llama3.2:3b",
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(url, json=data)

    result = response.json()

    ai_response = result["response"]

    print("AI:", ai_response)

    conversation.append("Msaidizi: " + ai_response)