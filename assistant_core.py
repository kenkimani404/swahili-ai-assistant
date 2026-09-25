import requests
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:3b"


SYSTEM_PROMPT = """
Wewe ni msaidizi wa chuo anayejibu kwa Kiswahili.

SHERIA MUHIMU:
1. Tumia taarifa zilizo kwenye CONTEXT pekee.
2. Usibuni taarifa kuhusu chuo.
3. Kama CONTEXT haitoshi kujibu swali, sema:
   "Samahani, sina taarifa hiyo kwenye mfumo."
4. Jibu kwa Kiswahili rahisi na kifupi.
5. Usiongeze namba, tarehe, majina au taratibu ambazo hazipo kwenye CONTEXT.
6. Lengo lako ni kueleza au kufupisha CONTEXT, si kubuni taarifa mpya.
"""


# --------------------------------------------------
# LOAD KNOWLEDGE BASE
# --------------------------------------------------

def load_knowledge():
    with open("knowledge.txt", "r", encoding="utf-8") as file:
        return [
            paragraph.strip()
            for paragraph in file.read().split("\n\n")
            if paragraph.strip()
        ]


documents = load_knowledge()


# --------------------------------------------------
# NORMALIZATION
# --------------------------------------------------

def normalize_word(word):
    word = word.lower().strip()

    # Remove punctuation
    word = re.sub(r"[^\w]", "", word)

    return word


# --------------------------------------------------
# SIMPLE KISWAHILI MORPHOLOGY
# --------------------------------------------------

def get_word_forms(word):
    word = normalize_word(word)

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

        "kitabu": {
            "kitabu",
            "vitabu"
        },

        "vitabu": {
            "kitabu",
            "vitabu"
        },

        "somo": {
            "somo",
            "masomo"
        },

        "masomo": {
            "somo",
            "masomo"
        },

        "mtihani": {
            "mtihani",
            "mitihani"
        },

        "mitihani": {
            "mtihani",
            "mitihani"
        },

        "ombi": {
            "ombi",
            "maombi",
            "kuomba"
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

        "sajili": {
            "sajili",
            "usajili",
            "kusajili"
        },

        "usajili": {
            "sajili",
            "usajili",
            "kusajili"
        },

        "kusajili": {
            "sajili",
            "usajili",
            "kusajili"
        },

        "attachment": {
            "attachment"
        },

        "maktaba": {
            "maktaba"
        },

        "ada": {
            "ada"
        }
    }

    return morphology_map.get(word, {word})


def analyze_morphology(question):
    words = question.lower().split()

    results = {}

    for word in words:
        clean_word = normalize_word(word)

        if not clean_word:
            continue

        forms = get_word_forms(clean_word)

        if len(forms) > 1:
            results[clean_word] = sorted(forms)

    return results


# --------------------------------------------------
# STOP WORDS
# --------------------------------------------------

STOP_WORDS = {
    "ni",
    "na",
    "ya",
    "wa",
    "za",
    "vya",
    "kwa",
    "katika",
    "hii",
    "hiyo",
    "hivi",
    "hivyo",
    "mimi",
    "wewe",
    "yeye",
    "sisi",
    "wao",
    "nina",
    "nini",
    "gani",
    "je",
    "kuhusu",
    "ina",
    "ana",
    "wana",
    "kwa",
    "mwanafunzi",
    "wanafunzi"
}


# --------------------------------------------------
# RETRIEVAL
# --------------------------------------------------

def retrieve_information(question):
    question_words = {
        normalize_word(word)
        for word in question.split()
        if normalize_word(word)
    }

    # Remove very common words
    meaningful_words = question_words - STOP_WORDS

    best_document = ""
    best_score = 0

    for document in documents:
        document_words = {
            normalize_word(word)
            for word in document.split()
            if normalize_word(word)
        }

        score = 0

        for word in meaningful_words:

            forms = get_word_forms(word)

            # Exact or morphological match
            if forms.intersection(document_words):
                score += 5

        if score > best_score:
            best_score = score
            best_document = document

    # Require meaningful evidence before using a document
    if best_score < 5:
        return "", 0

    return best_document, best_score


# --------------------------------------------------
# GENERATE ANSWER
# --------------------------------------------------

def generate_answer(question):

    morphology = analyze_morphology(question)

    context, score = retrieve_information(question)

    # No reliable information found
    if score == 0:
        return {
            "answer": "Samahani, sina taarifa hiyo kwenye mfumo.",
            "context": "",
            "score": 0,
            "morphology": morphology
        }

    prompt = f"""
CONTEXT:
{context}

SWALI:
{question}

Jibu swali kwa kutumia CONTEXT pekee.
"""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "system": SYSTEM_PROMPT,
        "stream": False,
        "options": {
            "temperature": 0.1
        }
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=120
        )

        response.raise_for_status()

        answer = response.json()["response"].strip()

    except Exception:
        answer = (
            "Samahani, kuna tatizo la kuwasiliana "
            "na mfumo wa AI."
        )

    return {
        "answer": answer,
        "context": context,
        "score": score,
        "morphology": morphology
    }