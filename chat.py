import os
from openai import OpenAI
from customer import CustomerProfile
from knowledge import KnowledgeBase
from prompts import build_system_prompt, parse_escalation, format_escalation_response

# Groq espone un'API compatibile OpenAI — stesso client, URL diverso
client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

MAX_HISTORY = 10  # messaggi (user+assistant) da tenere in contesto


class ChatSession:
    def __init__(self, customer: CustomerProfile, kb: KnowledgeBase):
        self.customer = customer
        self.kb = kb
        self.history: list[dict] = []

    def send(self, user_message: str) -> tuple[str, bool]:
        """
        Invia un messaggio e restituisce (risposta, is_escalation).
        """
        # 1. recupera i chunk di knowledge base più rilevanti per la domanda
        knowledge_context = self.kb.retrieve(user_message, top_k=4)

        # 2. costruisce il system prompt con profilo cliente + knowledge
        system_prompt = build_system_prompt(self.customer, knowledge_context)

        # 3. aggiunge il messaggio utente alla history
        self.history.append({"role": "user", "content": user_message})

        # 4. taglia la history per non sforare il context window
        trimmed_history = self.history[-MAX_HISTORY:]

        # 5. chiama il modello — API OpenAI-compatibile di Groq
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=1024,
            messages=[
                {"role": "system", "content": system_prompt},
                *trimmed_history,
            ],
        )

        # 6. estrae il testo dalla risposta
        raw = response.choices[0].message.content

        # 7. controlla se il modello ha deciso di escalare
        is_escalation, reason, clean_response = parse_escalation(raw)

        if is_escalation:
            final_response = format_escalation_response(reason, self.customer)
        else:
            final_response = clean_response

        # 8. salva la risposta in history per il turno successivo
        self.history.append({"role": "assistant", "content": raw})

        return final_response, is_escalation

    def reset(self):
        self.history = []
