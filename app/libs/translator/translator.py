import json
import asyncio
from ollama import AsyncClient  # type: ignore
from app.libs.webscraping.extractor import extract_from_html
from app.libs.webscraping.scrapper import AsyncFindChipsScraper
from app.log.logger import logger


class TranslatorService:
    """Handles translation of product descriptions using the Ollama model."""

    def __init__(self, model_name: str = "translator:latest"):
        self.model_name = model_name
        self.client = AsyncClient()

    async def translate_text(self, text: str) -> str:
        """Send the text to Ollama for translation."""
        if not text or text.strip().lower() == "n/a":
            return "N/A"

        prompt = (
            "Traduza a seguinte descrição técnica de componente eletrônico para o português brasileiro, "
            "mantendo as unidades, símbolos e formato técnico. "
            "Responda somente com a tradução final, sem incluir raciocínio, explicações ou texto entre tags <think>.\n\n"
            f"Descrição original:\n{text.strip()}"
        )

        try:
            response = await self.client.generate(
                model=self.model_name,
                prompt=prompt,
                stream=False,
            )
            translated = response["response"].strip()

            # Remove reasoning section if present
            if "<think>" in translated:
                import re
                translated = re.sub(r"<think>.*?</think>", "", translated, flags=re.DOTALL).strip()

            return translated
        except Exception as e:
            logger.warning(f"[TRANSLATOR] Failed to translate text: {e}")
            return text


async def run_translation_pipeline():
    """Scrape → Extract → Translate all descriptions."""
    pns = [
        "CL10C330JB8NNNC",
        "CL10B472KB8NNNC",
        "GRM1885C1H180JA01D",
        "CL10A106KP8NNNC",
        "C1608X5R1E106M080AC",
        "NACE100M100V6.3X8TR13F",
        "CRCW060320K0FKEA",
    ]
    target_supplier = "Avnet"

    async with AsyncFindChipsScraper(max_concurrency=4, sleep_between=1.0) as scraper:
        html_by_pn = await scraper.fetch_many(pns)

    translator = TranslatorService(model_name="translator:latest")

    for pn, html in html_by_pn.items():
        extracted_json = extract_from_html(html, target_supplier)

        if not extracted_json or not extracted_json.strip().startswith("{"):
            logger.warning(f"[TRANSLATOR] Skipping PN {pn}: invalid extraction output.")
            continue

        try:
            data = json.loads(extracted_json)
        except json.JSONDecodeError as e:
            logger.warning(f"[TRANSLATOR] Could not decode JSON for {pn}: {e}")
            continue

        description_en = data.get("description", "N/A")

        # Translate only the description
        translated_desc = await translator.translate_text(description_en)
        data["description_pt"] = translated_desc

        # ✅ Apenas imprime as descrições
        print(f"\nEN: {data['description']}")
        print(f"PT: {data['description_pt']}")
        print("-" * 80)


if __name__ == "__main__":
    asyncio.run(run_translation_pipeline())
