import logging
import threading
import uuid
import torch
import gc
import os
import psutil
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
#  Language Detection
# ─────────────────────────────────────────────

ARABIC_CHARS = set("ابتثجحخدذرزسشصضطظعغفقكلمنهوي")

def detect_language(text: str) -> str:
    arabic_count = sum(1 for c in text if c in ARABIC_CHARS)
    return "ar" if arabic_count > len(text) * 0.2 else "en"


# ─────────────────────────────────────────────
#  Text Normalisation
# ─────────────────────────────────────────────

def _normalise(text: str) -> str:
    """Lowercase + normalise Arabic alef/teh marbuta/alef maqsura variants."""
    return (
        text.lower()
        .replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
        .replace("ى", "ي").replace("ة", "ه")
    )


# ─────────────────────────────────────────────
#  Conversation Memory
# ─────────────────────────────────────────────

@dataclass
class ChatState:
    history: List[Dict[str, str]] = field(default_factory=list)
    last_intent: Optional[str] = None
    last_product: Optional[Dict[str, Any]] = None
    awaiting_confirmation: bool = False
    pending_order_product: Optional[Dict[str, Any]] = None
    language: str = "ar"
    clarification_attempts: int = 0

    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})
        if len(self.history) > 20:
            self.history = self.history[-20:]

    def reset_order_flow(self):
        self.awaiting_confirmation = False
        self.pending_order_product = None
        self.clarification_attempts = 0

    def update_last_product(self, product: Optional[Dict[str, Any]]):
        if product:
            self.last_product = product

    def to_prompt_history(self) -> str:
        if not self.history:
            return "No previous messages."
        lines = []
        for msg in self.history[-10:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            lines.append(f"{role}: {msg['content']}")
        return "\n".join(lines)


# ── Per-user state registry ───────────────────

_user_states: Dict[str, ChatState] = {}


def get_chat_state(user_id: Optional[int], session_token: Optional[str] = None) -> ChatState:
    if user_id:
        key = f"user:{user_id}"
    elif session_token:
        key = f"anon:{session_token}"
    else:
        return ChatState()

    if key not in _user_states:
        _user_states[key] = ChatState()
    return _user_states[key]


# ─────────────────────────────────────────────
#  Keyword / Phrase Sets
# ─────────────────────────────────────────────

VAGUE_REFERENCES = {
    "it", "this", "that", "the product", "this one", "that one",
    "ده", "دى", "دا", "المنتج ده", "نفسه", "نفس المنتج",
}

# Arabic root substrings — matched anywhere in the normalised text
ARABIC_ORDER_ROOTS = ["اطلب", "اشتري", "اشترى", "طلب", "شراء", "شري"]

ORDER_TRIGGERS = {
    "order", "buy", "purchase", "i want it", "i'll take it", "i want this",
    "i want to order", "i want to buy",
    "اطلب", "شراء", "عايز اطلب", "اشتري", "خده", "طلب", "عايزه", "اطلبه",
    "ممكن اطلب", "عايز اشتري", "عايزة اشتري", "عايزة اطلب",
    "عايز اطلبه", "عايزة اطلبه", "عايز اشتريه", "عايزة اشتريه",
    "حابب اطلب", "حابه اطلب", "نفسي اطلب",
}

DETAIL_TRIGGERS = {
    "tell me more", "more details", "details", "more info", "what is it",
    "describe", "features", "specs", "info", "information",
    "اعرف أكتر", "اعرف اكتر", "تفاصيل", "وصف", "عن المنتج",
    "إيه ده", "ايه ده", "عايز اعرف", "قولي عنه",
}

CONFIRMATION_YES = {
    "yes", "yeah", "yep", "sure", "confirm", "ok", "okay", "of course",
    "أيوه", "ايوه", "تمام", "موافق", "اه", "أكيد", "اكيد",
    "اوكيه", "يلا", "ماشي", "طيب", "عيني",
}

CONFIRMATION_NO = {
    "no", "nope", "cancel", "never mind", "stop", "dont", "don't",
    "لا", "لأ", "الغ", "إلغ", "مش عايز", "مش عايزة", "بلاش", "لا شكرا",
}

GREETING_TRIGGERS = {
    "hi", "hello", "hey", "good morning", "good evening", "howdy",
    "أهلا", "اهلا", "مرحبا", "سلام", "هاي", "هلو",
    "صباح الخير", "مساء الخير", "ازيك", "ازيكم", "كيف حالك", "هلا",
}

PRODUCT_LIST_TRIGGERS = {
    "what products", "show products", "list products", "what do you have",
    "what do you sell", "show me", "all products", "available products",
    "إيه المنتجات", "ايه المنتجات", "عندك إيه", "عندك ايه",
    "اعرض المنتجات", "شوفلي", "كل المنتجات",
    "ايه اللي عندك", "عايز أشوف", "عايز اشوف",
}


# ─────────────────────────────────────────────
#  Matching Helpers
# ─────────────────────────────────────────────

def _contains_any(text: str, phrases: set) -> bool:
    """
    Phrase-set membership check with Arabic normalisation.
    Matches both whole tokens and substrings.
    """
    norm = _normalise(text)
    tokens = set(norm.split())
    for phrase in phrases:
        p = _normalise(phrase)
        if p in norm or p in tokens:
            return True
    return False


def _is_order_intent(text: str) -> bool:
    """
    Dedicated order-intent detector that catches:
    - All entries in ORDER_TRIGGERS (phrase-set match)
    - Direct Arabic root substrings: اطلب / شراء / طلب …
    - Combined vague + order: "اطلبه" / "I want it"
    """
    if _contains_any(text, ORDER_TRIGGERS):
        return True
    norm = _normalise(text)
    for root in ARABIC_ORDER_ROOTS:
        if root in norm:
            return True
    return False


# ─────────────────────────────────────────────
#  Response String Helpers  (bilingual)
# ─────────────────────────────────────────────

def _t(lang: str, ar: str, en: str) -> str:
    return ar if lang == "ar" else en


def _greeting_response(lang: str) -> str:
    return _t(
        lang,
        "أهلاً وسهلاً! 👋 أنا MediCare AI، مساعدك في المنتجات الطبية. إزاي أقدر أساعدك النهارده؟",
        "Welcome! 👋 I'm MediCare AI, your medical products assistant. How can I help you today?",
    )


def _product_list_response(products: List[Dict], lang: str) -> str:
    if not products:
        return _t(
            lang,
            "معلش، مفيش منتجات متاحة دلوقتي. حاول تاني بعد شوية. 🙏",
            "Sorry, no products are available right now. Please try again later. 🙏",
        )
    header = _t(lang, "تفضل، ده بعض المنتجات المتاحة 🏥:\n", "Here are some of our available products 🏥:\n")
    footer = _t(
        lang,
        "\nقولي لو عايز تعرف أكتر عن أي منتج أو تطلبه! 😊",
        "\nLet me know if you'd like details or want to order anything! 😊",
    )
    lines = [header]
    for p in products[:5]:
        lines.append(f"  {p.get('emoji', '📦')} *{p['name']}* — {p['price']} {p.get('currency', 'EGP')}")
    lines.append(footer)
    return "\n".join(lines)


def _recommendation_response(product: Dict, lang: str) -> str:
    emoji = product.get("emoji", "📦")
    name, price, currency = product["name"], product["price"], product.get("currency", "EGP")
    desc = product.get("description", "")
    follow_up = _t(lang, "تحب تعرف أكتر أو تطلبه؟ 😊", "Would you like more details or to order it? 😊")
    if lang == "ar":
        return f"بناءً على طلبك، بنصحك بـ {emoji} *{name}* بسعر {price} {currency}.\n{desc}\n\n{follow_up}"
    return f"Based on your request, I recommend {emoji} *{name}* for {price} {currency}.\n{desc}\n\n{follow_up}"


def _detail_response(product: Dict, lang: str) -> str:
    emoji = product.get("emoji", "📦")
    name, price, currency = product["name"], product["price"], product.get("currency", "EGP")
    desc = product.get("description", _t(lang, "لا توجد تفاصيل إضافية.", "No additional details available."))
    follow_up = _t(lang, "تحب تطلبه؟ قولي وهجهزه ليك! 🛒", "Want to order it? Just say the word! 🛒")
    if lang == "ar":
        return f"تفاصيل {emoji} *{name}*:\n\n{desc}\n💰 السعر: {price} {currency}\n\n{follow_up}"
    return f"Details for {emoji} *{name}*:\n\n{desc}\n💰 Price: {price} {currency}\n\n{follow_up}"


def _order_confirmation_request(product: Dict, lang: str) -> str:
    emoji = product.get("emoji", "📦")
    name, price, currency = product["name"], product["price"], product.get("currency", "EGP")
    if lang == "ar":
        return f"تمام! 👌 هتطلب {emoji} *{name}* بسعر {price} {currency}.\nتأكيد الطلب؟ (أيوه / لا)"
    return f"Great! 👌 You're ordering {emoji} *{name}* for {price} {currency}.\nConfirm? (yes / no)"


def _order_success_response(product: Dict, lang: str) -> str:
    emoji, name = product.get("emoji", "📦"), product["name"]
    if lang == "ar":
        return (
            f"🎉 تم تسجيل طلبك لـ {emoji} *{name}* بنجاح!\n"
            f"فريقنا هيتواصل معاك قريبًا لتأكيد التوصيل. شكرًا! 💙"
        )
    return (
        f"🎉 Your order for {emoji} *{name}* has been placed!\n"
        f"Our team will contact you soon to confirm delivery. Thank you! 💙"
    )


def _order_failed_response(lang: str) -> str:
    return _t(
        lang,
        "حصل مشكلة في تسجيل الطلب. ممكن تحاول تاني أو تتواصل مع الدعم. 🙏",
        "There was a problem placing your order. Please try again or contact support. 🙏",
    )


def _order_cancelled_response(lang: str) -> str:
    return _t(
        lang,
        "تمام، تم إلغاء الطلب. في أي وقت تحتاج حاجة، أنا هنا! 😊",
        "Order cancelled. I'm here whenever you need help! 😊",
    )


def _order_clarification_response(lang: str) -> str:
    return _t(
        lang,
        "أي منتج تحب تطلبه؟ قولي اسمه أو اطلب مني أقترح حاجة. 😊",
        "Which product would you like to order? Tell me its name or ask for a recommendation. 😊",
    )


def _no_product_context_response(lang: str) -> str:
    return _t(
        lang,
        "مش عارف أي منتج بتقصد. ممكن تقولي اسمه أو تطلب مني أقترح حاجة؟ 🤔",
        "I'm not sure which product you mean. Could you tell me the name or ask for a suggestion? 🤔",
    )


def _reask_confirmation_response(product: Dict, lang: str) -> str:
    name = product["name"]
    if lang == "ar":
        return f"مش فاهم ردك. تأكيد الطلب لـ *{name}*؟ (أيوه / لا)"
    return f"I didn't catch that. Confirm order for *{name}*? (yes / no)"


def _too_many_reasks_response(lang: str) -> str:
    return _t(
        lang,
        "يبدو إن فيه لبس. تم إلغاء الطلب تلقائيًا. قولي لو عايز تبدأ من أول! 😊",
        "Seems like there's some confusion. Order cancelled automatically. Let me know if you'd like to start over! 😊",
    )


def _fallback_response(intent: str, lang: str) -> str:
    if lang == "ar":
        mapping = {
            "greeting": "أهلاً! 👋 كيف أقدر أساعدك؟",
            "purchase": "يلا نكمل طلبك! 🛒 إيه المنتج اللي عايزه؟",
            "inquiry":  "أنا هنا أساعدك. ممكن تسألني عن أي منتج طبي! 💊",
        }
    else:
        mapping = {
            "greeting": "Hello! 👋 How can I help you?",
            "purchase": "Let's complete your order! 🛒 Which product are you looking for?",
            "inquiry":  "I'm here to help with any medical product questions! 💊",
        }
    return mapping.get(intent, _t(lang,
        "مش فاهم قصدك. ممكن توضح أكتر؟ 🙏",
        "I didn't quite understand. Could you clarify? 🙏",
    ))


# ─────────────────────────────────────────────
#  LLM-based Response Builder
# ─────────────────────────────────────────────

SYSTEM_PROMPT_TEMPLATE = """You are MediCare AI 🏥, a friendly and conversational medical products assistant.
You remember previous messages and help users step by step.
Always respond ONLY in {lang_instruction}.
Keep responses short (2–4 sentences), warm, and helpful. Use emojis sparingly.
Never invent product details — only reference the context provided.

Conversation so far:
{history}

Current context:
- Last detected intent: {intent}
- Last recommended product: {last_product}
- User sentiment: {sentiment}

Respond naturally to the user's latest message.
Do NOT greet again if the conversation is already ongoing.
Do NOT suggest ordering unless the user explicitly asks."""


def _build_llm_response(
    message: str,
    state: ChatState,
    intent: str,
    sentiment: str,
    recommendations: List[Dict],
    model,
    lang: str,
) -> str:
    """Call the LLM response model. Returns '' on failure or short/empty output."""
    lang_instruction = "Arabic (Egyptian dialect)" if lang == "ar" else "English"
    last_product_str = (
        f"{state.last_product['name']} ({state.last_product['price']} "
        f"{state.last_product.get('currency', 'EGP')})"
        if state.last_product else "None"
    )
    system = SYSTEM_PROMPT_TEMPLATE.format(
        lang_instruction=lang_instruction,
        history=state.to_prompt_history(),
        intent=intent,
        last_product=last_product_str,
        sentiment=sentiment,
    )
    context = {
        "intent": intent,
        "sentiment": sentiment,
        "recommendations": recommendations,
        "system_prompt": system,
    }
    try:
        if model:
            result = model.generate(message, context)
            response = result.get("response", "").strip()
            if len(response) >= 10:
                return response
    except Exception as e:
        logger.error(f"LLM response generation error: {e}")
    return ""


# ─────────────────────────────────────────────
#  Order Creation Helper
# ─────────────────────────────────────────────

def _create_order(user_id: Optional[int], product: Dict) -> bool:
    try:
        from django.apps import apps
        Order = apps.get_model("orders", "Order")
        OrderItem = apps.get_model("orders", "OrderItem")
        Product = apps.get_model("products", "Product")

        product_obj = Product.objects.get(id=product["product_id"])
        order = Order.objects.create(user_id=user_id, status="pending")
        OrderItem.objects.create(
            order=order,
            product=product_obj,
            quantity=1,
            price=product_obj.price,
        )
        logger.info(f"Order created: order_id={order.id}, product={product_obj.name}")
        return True
    except Exception as e:
        logger.error(f"Order creation failed: {e}")
        return False


# ─────────────────────────────────────────────
#  Main Orchestrator
# ─────────────────────────────────────────────

class ModelOrchestrator:
    _instance = None
    _models: Dict[str, Any] = {}

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        logger.info("Initializing MediCare AI Orchestrator...")
        self._initialized = True
        self._models_ready = False
        thread = threading.Thread(target=self._preload_models, daemon=True)
        thread.start()

    # ── Model Loading ─────────────────────────

    def _preload_models(self):
        try:
            logger.info("Background: loading recommendation model...")
            self._get_model("recommendation")
            self._models_ready = True
            logger.info("Background: all models ready ✓")
        except Exception as e:
            logger.error(f"Background model load failed: {e}")

    def _get_model(self, model_type: str):
        if model_type in self._models and self._models[model_type] is not None:
            return self._models[model_type]
        try:
            available_ram_gb = psutil.virtual_memory().available / (1024 ** 3)

            if model_type == "recommendation":
                from assistify.ml_models.product_recommendation.model import ProductRecommendationModel
                self._models["recommendation"] = ProductRecommendationModel()
                return self._models["recommendation"]

            force_ml = os.environ.get("FORCE_ML", "False").lower() == "true"
            threshold = 0.5 if force_ml else 1.5

            if available_ram_gb < threshold:
                logger.warning(f"Low memory ({available_ram_gb:.2f}GB). Skipping {model_type}.")
                return None

            if model_type == "intent":
                from assistify.ml_models.intent_classification.model import IntentClassificationModel
                self._models["intent"] = IntentClassificationModel()
            elif model_type == "sentiment":
                from assistify.ml_models.sentiment_analysis.model import SentimentAnalysisModel
                self._models["sentiment"] = SentimentAnalysisModel()
            elif model_type == "response":
                from assistify.ml_models.response_generation.model import ResponseGenerationModel
                self._models["response"] = ResponseGenerationModel()

            return self._models.get(model_type)
        except Exception as e:
            logger.error(f"Failed to load {model_type} model: {e}", exc_info=True)
            return None

    # ── Main Entry Point ──────────────────────

    def process_message(
        self,
        message: str = "",
        user_id: Optional[int] = None,
        session_token: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:

        text = (message or kwargs.get("text", "")).strip()
        if not text:
            return {"success": False, "error": "Empty message"}

        logger.info(f"[user={user_id}] Processing: {text}")

        state = get_chat_state(user_id, session_token)
        lang = detect_language(text)
        state.language = lang
        state.add_message("user", text)

        # ═══════════════════════════════════════
        #  PRIORITY 1 — Active order confirmation
        #  LLM must NEVER run inside this block.
        # ═══════════════════════════════════════
        if state.awaiting_confirmation:
            response = self._handle_confirmation(text, state, user_id, lang)
            state.add_message("assistant", response)
            return self._build_result(response, state)

        # ── Shared classification ──
        intent_data = self._classify_intent_safe(text)
        sentiment_data = self._analyze_sentiment_safe(text)
        intent = intent_data["intent"]
        sentiment = sentiment_data["sentiment"]
        state.last_intent = intent

        # ═══════════════════════════════════════
        #  PRIORITY 2 — Greeting
        # ═══════════════════════════════════════
        if _contains_any(text, GREETING_TRIGGERS) or intent == "greeting":
            response = _greeting_response(lang)
            state.add_message("assistant", response)
            return self._build_result(response, state, intent_data, sentiment_data)

        # ═══════════════════════════════════════
        #  PRIORITY 3 — Product listing
        # ═══════════════════════════════════════
        if _contains_any(text, PRODUCT_LIST_TRIGGERS):
            products, method = self._get_recommendations_stable(
                user_id=user_id, intent=intent, query=text
            )
            if products:
                state.update_last_product(products[0])
            response = _product_list_response(products, lang)
            state.add_message("assistant", response)
            return self._build_result(response, state, intent_data, sentiment_data, products, method)

        # ═══════════════════════════════════════
        #  PRIORITY 4 — Order intent
        #
        #  Unified handler covers ALL cases:
        #    a) Direct:  "order", "اطلب", "شراء", "طلب"
        #    b) Vague+:  "اطلبه", "I want it", "خده"
        #    c) Polite:  "ممكن اطلب", "عايزة اشتري"
        #    d) Root:    any text containing اطلب / شراء …
        #
        #  NOTE: VAGUE_REFERENCES restriction has been removed —
        #  vague inputs that imply ordering are handled here too.
        # ═══════════════════════════════════════
        if _is_order_intent(text):
            response = self._handle_order_request(text, state, user_id, lang, intent)
            state.add_message("assistant", response)
            return self._build_result(response, state, intent_data, sentiment_data)

        # ═══════════════════════════════════════
        #  PRIORITY 5 — Follow-up / vague reference (non-order)
        # ═══════════════════════════════════════
        is_vague = _contains_any(text, VAGUE_REFERENCES)
        is_detail = _contains_any(text, DETAIL_TRIGGERS)

        if (is_vague or is_detail) and state.last_product:
            response = _detail_response(state.last_product, lang)
            state.add_message("assistant", response)
            return self._build_result(response, state, intent_data, sentiment_data)

        if (is_vague or is_detail) and not state.last_product:
            response = _no_product_context_response(lang)
            state.add_message("assistant", response)
            return self._build_result(response, state, intent_data, sentiment_data)

        # ═══════════════════════════════════════
        #  PRIORITY 6 — Product recommendation
        # ═══════════════════════════════════════
        products, method = self._get_recommendations_stable(
            user_id=user_id, intent=intent, query=text
        )
        if products:
            state.update_last_product(products[0])

        rule_response = _recommendation_response(products[0], lang) if products else ""

        # ═══════════════════════════════════════
        #  PRIORITY 7 — LLM (last resort only)
        #  Explicitly blocked when order flow is active.
        # ═══════════════════════════════════════
        llm_response = ""
        if not state.awaiting_confirmation:
            response_model = self._get_model("response")
            llm_response = _build_llm_response(
                text, state, intent, sentiment, products, response_model, lang
            )

        response = llm_response or rule_response or _fallback_response(intent, lang)
        state.add_message("assistant", response)

        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        return self._build_result(response, state, intent_data, sentiment_data, products, method)

    # ── Order Request Handler ──────────────────

    def _handle_order_request(
        self,
        text: str,
        state: ChatState,
        user_id: Optional[int],
        lang: str,
        intent: str,
    ) -> str:
        """
        Resolve the target product and move to confirmation.

        Priority:
          1. last_product already in context
          2. recommendation engine result
          3. ask clarification
        """
        if state.last_product:
            state.awaiting_confirmation = True
            state.pending_order_product = state.last_product
            return _order_confirmation_request(state.last_product, lang)

        products, _ = self._get_recommendations_stable(
            user_id=user_id, intent=intent, query=text
        )
        if products:
            state.update_last_product(products[0])
            state.awaiting_confirmation = True
            state.pending_order_product = products[0]
            return _order_confirmation_request(products[0], lang)

        return _order_clarification_response(lang)

    # ── Order Confirmation Handler ─────────────

    def _handle_confirmation(
        self,
        text: str,
        state: ChatState,
        user_id: Optional[int],
        lang: str,
    ) -> str:
        if _contains_any(text, CONFIRMATION_YES):
            product = state.pending_order_product
            state.reset_order_flow()
            return (
                _order_success_response(product, lang)
                if _create_order(user_id, product)
                else _order_failed_response(lang)
            )

        if _contains_any(text, CONFIRMATION_NO):
            state.reset_order_flow()
            return _order_cancelled_response(lang)

        # Ambiguous — re-ask, capped at 3 attempts
        state.clarification_attempts += 1
        if state.clarification_attempts >= 3:
            state.reset_order_flow()
            return _too_many_reasks_response(lang)

        return _reask_confirmation_response(state.pending_order_product, lang)

    # ── Recommendation Engine ──────────────────

    def _get_recommendations_stable(
        self,
        user_id: Optional[int],
        intent: str,
        query: str,
    ) -> Tuple[List[Dict], str]:
        method = "fallback_database_search"
        recs: List[Dict] = []

        try:
            model = self._get_model("recommendation")
            if model:
                rec_result = model.predict(user_id=user_id, query=query, intent=intent)
                recs = rec_result.get("recommendations", [])
                method = rec_result.get("method", "ml_recommendation")
        except Exception as e:
            logger.error(f"Recommendation model error: {e}")

        if not recs:
            try:
                from django.apps import apps
                from django.db.models import Q
                Product = apps.get_model("products", "Product")

                tokens = [t for t in query.split() if len(t) > 2]
                name_q = Q()
                desc_q = Q()
                for token in tokens:
                    name_q |= Q(name__icontains=token)
                    desc_q |= Q(description__icontains=token)

                qs = Product.objects.filter(is_active=True).filter(name_q | desc_q).distinct()
                if not qs.exists():
                    qs = Product.objects.filter(is_active=True).order_by("name")[:5]

                recs = [
                    {
                        "product_id": p.id,
                        "name": p.name,
                        "price": float(p.price),
                        "currency": getattr(p, "currency", "EGP"),
                        "description": p.description or "",
                        "emoji": getattr(p, "emoji", None) or "📦",
                        "score": 0.5,
                    }
                    for p in qs[:5]
                ]
                method = "database_fallback"
            except Exception as e:
                logger.error(f"DB search failed: {e}")

        return recs, method

    # ── Safe Wrappers ─────────────────────────

    def _classify_intent_safe(self, message: str) -> Dict[str, Any]:
        try:
            model = self._get_model("intent")
            if model:
                return model.predict(message)
        except Exception as e:
            logger.error(f"Intent prediction error: {e}")
        return self._fallback_intent(message)

    def _analyze_sentiment_safe(self, message: str) -> Dict[str, Any]:
        try:
            model = self._get_model("sentiment")
            if model:
                return model.predict(message)
        except Exception as e:
            logger.error(f"Sentiment prediction error: {e}")
        return self._fallback_sentiment(message)

    # ── Fallbacks ─────────────────────────────

    def _fallback_intent(self, text: str) -> Dict[str, Any]:
        if _is_order_intent(text):
            return {"intent": "purchase", "confidence": 0.5, "label_idx": 7}
        if _contains_any(text, GREETING_TRIGGERS):
            return {"intent": "greeting", "confidence": 0.5, "label_idx": 0}
        return {"intent": "inquiry", "confidence": 0.1, "label_idx": 1}

    def _fallback_sentiment(self, text: str) -> Dict[str, Any]:
        t = text.lower()
        if any(w in t for w in ["good", "great", "thanks", "جيد", "شكرا", "تمام"]):
            return {"sentiment": "positive", "confidence": 0.5, "label_idx": 2}
        if any(w in t for w in ["bad", "poor", "issue", "سيء", "مشكلة"]):
            return {"sentiment": "negative", "confidence": 0.5, "label_idx": 0}
        return {"sentiment": "neutral", "confidence": 0.1, "label_idx": 1}

    # ── Result Builder ────────────────────────

    def _build_result(
        self,
        response: str,
        state: ChatState,
        intent_data: Optional[Dict] = None,
        sentiment_data: Optional[Dict] = None,
        recommendations: Optional[List] = None,
        rec_method: str = "unknown",
    ) -> Dict[str, Any]:
        intent_data = intent_data or {"intent": state.last_intent or "inquiry", "confidence": 0.0}
        sentiment_data = sentiment_data or {"sentiment": "neutral", "confidence": 0.0}
        recommendations = recommendations or []
        return {
            "success": True,
            "response": response,
            "intent": intent_data["intent"],
            "sentiment": sentiment_data["sentiment"],
            "recommendations": recommendations,
            "intent_confidence": intent_data.get("confidence", 0.0),
            "sentiment_confidence": sentiment_data.get("confidence", 0.0),
            "metadata": {
                "intent_label_idx": intent_data.get("label_idx"),
                "sentiment_label_idx": sentiment_data.get("label_idx"),
                "response_confidence": 0.0,
                "recommendation_method": rec_method,
                "last_product": state.last_product,
                "awaiting_confirmation": state.awaiting_confirmation,
                "language": state.language,
            },
        }

    # ── Status ────────────────────────────────

    def get_model_status(self) -> Dict[str, Any]:
        available_ram_gb = psutil.virtual_memory().available / (1024 ** 3)
        return {
            "status": "operational",
            "memory_available_gb": round(available_ram_gb, 2),
            "models_loaded": list(self._models.keys()),
            "active_sessions": len(_user_states),
            "models_ready": self._models_ready,
        }
    