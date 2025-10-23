import asyncio
from app.libs.ncm import setup
from app.libs.websocket.manager import ws_manager
from app.services.extract_service.enterPDF import EnterPDF
# from app.services.ollama_service.generate_final_desc import Generate_final_desc


class PipelineManager:
    def __init__(self, pdf_bytes: str):
        self._pdf_bytes = pdf_bytes
        self.extracted_data = None

    async def _notify(self, process: str, status: str) -> dict:
        payload = {
            "process": process,
            "status": status,
        }

        return await ws_manager.send_json(payload)

    async def _pdf_step(self) -> None:
        await self._notify("pdf_extraction", "in_progress")
        processer = EnterPDF(self._pdf_bytes)
        pdf_data = await asyncio.to_thread(processer.process_enter)
        self._pdf_data = pdf_data
        await self._notify("pdf_extraction", "success")

    async def _web_scrapping(self) -> None:
        await self._notify('web_scrapping', 'in_progress')
        print('webscraping executado')
        await self._notify('web_scrapping', 'success')

    async def _get_ncm(self) -> None:
        await self._notify("get_ncms", "in_progress")

        query = "LED Verde, 2 mm SMD"

        self._ncm_founded = await setup.get_ncm(query)

        await self._notify("get_ncms", "success")

    async def _get_final_description(self) -> None:
        await self._notify("product_description", "in_progress")

        print('gerou descrição final')
        await self._notify("product_description", "success")

    async def run(self) -> None:
        try:
            await self._notify('process_pipeline', 'started')
            await self._pdf_step()
            await self._web_scrapping()
            await self._get_ncm()
            await self._get_final_description()
            # print('self._ncm_founded', self._ncm_founded)
            # print('self._pdf_data', self._pdf_data)
            await self._notify('process_overall', 'finished')
        except Exception as e:
            await self._notify("pipeline_overall", "failed", {"error": str(e)})
            raise
