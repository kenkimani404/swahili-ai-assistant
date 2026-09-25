import requests
import re

# -----------------------------------
# OLLAMA CONNECTION
# -----------------------------------

url = "http://localhost:11434/api/generate"

system_prompt = """
Wewe ni Swahili Path Campus Assistant.

Unasaidia wanafunzi kupata taarifa za chuo kwa Kiswahili rahisi.

Tumia CONTEXT uliyopewa kujibu swali.
Usibuni taarifa ambazo hazipo kwenye CONTEXT.

Ikiwa taarifa haipo kwenye CONTEXT, sema:
"Samahani, sina taarifa hiyo kwenye mfumo."

Jibu kwa ufupi na kwa uwazi.
"""


# -----------------------------------
# LOAD KNOWLEDGE BASE
# -----------------------------------

with open("knowledge.txt", "r", encoding="utf-8") as file:
    knowledge = file.read()

documents = knowledge.split("\n\n")


# -----------------------------------
# SIMPLE KISWAHILI MORPHOLOGY
# -----------------------------------

def normalize_word(word):
    word = word.lower().strip()
    word = re.sub(r"[^\w]", "", word)

    prefixes = [
        "wana", "mwana", "wa", "ma",
        "ki", "vi", "mi", "mu",
        "ku", "ka", "na", "ni",
        "ana", "ame", "wame",
        "m", "u"
    ]

    for prefix in prefixes:
        if word.startswith(prefix) and len(word) - len(prefix) >= 3:
            word = word[len(prefix):]
            break

    return word


def get_word_forms(word):
    """
    Creates simple morphological variants of a Swahili word.

    This is a rule-based MVP, not a complete
    Kiswahili morphological analyzer.
    """

    word = word.lower()

    forms = {word}

    morphology_map = {

        "mwanafunzi": {
            "mwanafunzi",
            "wanafunzi"
        },

        "wanafunzi": {
            "mwanafunzi",
            "wanafunzi"
        },

        "mwalimu": {
            "mwalimu",
            "walimu"
        },

        "walimu": {
            "mwalimu",
            "walimu"
        },

        "attachment": {
            "attachment"
        },

        "maombi": {
            "ombi",
            "maombi",
            "kuomba"
        },

        "kuomba": {
            "ombi",
            "maombi",
            "kuomba"
        },

        "wanahitaji": {
            "hitaji",
            "wanahitaji",
            "unahitaji",
            "nahitaji"
        },

        "unahitaji": {
            "hitaji",
            "unahitaji",
            "wanahitaji"
        },

        "nahitaji": {
            "hitaji",
            "nahitaji",
            "wanahitaji"
        },

        "usajili": {
            "usajili",
            "sajili",
            "kusajili"
        },

        "kusajili": {
            "usajili",
            "sajili",
            "kusajili"
        },

        "mitihani": {
            "mtihani",
            "mitihani"
        },

        "mtihani": {
            "mtihani",
            "mitihani"
        },

        "maktaba": {
            "maktaba"
        },

        "vitabu": {
            "kitabu",
            "vitabu"
        },

        "kitabu": {
            "kitabu",
            "vitabu"
        },

        "ada": {
            "ada"
        },

        "masomo": {
            "somo",
            "masomo"
        },

        "somo": {
            "somo",
            "masomo"
        }
    }

    if word in morphology_map:
        forms.update(morphology_map[word])

    normalized = normalize_word(word)

    if normalized:
        forms.add(normalized)

    return forms


# -----------------------------------
# SHOW MORPHOLOGY
# -----------------------------------

def show_morphology(question):

    words = re.findall(r"\b\w+\b", question.lower())

    print("\n--- Morphology Analysis ---")

    for word in words:

        forms = get_word_forms(word)

        if len(forms) > 1:
            print(
                f"{word} -> {', '.join(forms)}"
            )

    print("---------------------------\n")


# -----------------------------------
# RETRIEVAL
# -----------------------------------

def retrieve_information(question):

    question_words = re.findall(
        r"\b\w+\b",
        question.lower()
    )

    expanded_words = set()

    for word in question_words:

        expanded_words.update(
            get_word_forms(word)
        )

    best_document = ""
    best_score = 0

    for document in documents:

        document_words = re.findall(
            r"\b\w+\b",
            document.lower()
        )

        score = 0

        for query_word in expanded_words:

            for document_word in document_words:

                if query_word == document_word:

                    score += 2

                elif len(query_word) >= 4 and (
                    query_word in document_word
                    or document_word in query_word
                ):

                    score += 1

        if score > best_score:

            best_score = score
            best_document = document

    return best_document, best_score


# -----------------------------------
# CHAT APPLICATION
# -----------------------------------

print("======================================")
print("   SWAHILI PATH CAMPUS ASSISTANT")
print("======================================")
print("Andika 'exit' kuondoka.")
print()


while True:

    user_input = input("You: ")

    # Exit before running morphology
    if user_input.lower() == "exit":

        print("Kwaheri!")
        break

    # Show morphology for demonstration
    show_morphology(user_input)

    # Retrieve relevant campus information
    context, score = retrieve_information(
        user_input
    )

    # If nothing relevant was found
    if score == 0:

        context = (
            "Hakuna taarifa inayohusiana "
            "na swali hili kwenye knowledge base."
        )

    # Debugging information
    print("Retrieved context:")
    print(context)
    print("Retrieval score:", score)
    print()

    # Create prompt for LLaMA
    prompt = f"""
Wewe ni Swahili Path Campus Assistant.

Jibu swali la mwanafunzi kwa kutumia TAARIFA ILIYO KWENYE CONTEXT PEKEE.

KANUNI MUHIMU:
1. Usiongeze taarifa yoyote ambayo haipo kwenye CONTEXT.
2. Usibuni au kukisia majibu.
3. Ikiwa jibu halipo kwenye CONTEXT, sema:
"Samahani, sina taarifa hiyo kwenye mfumo."
4. Usirudie swali la mwanafunzi.
5. Jibu kwa Kiswahili rahisi na kwa ufupi.

CONTEXT:
{context}

SWALI:
{user_input}

JIBU:
"""

    # Send request to Ollama
    data = {

        "model": "llama3.2:3b",

        "prompt": prompt,

        "stream": False
    }

    response = requests.post(
        url,
        json=data
    )

    result = response.json()

    # Display AI response
    print("AI:", result["response"])
    print()