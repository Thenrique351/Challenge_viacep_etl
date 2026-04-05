import asyncio
import aiohttp


class ViaCepExtractor:
    def __init__(self, max_concurrent_requests=50, max_retries=3):
        # Controle de concorrência para otimizar sem bloquear o IP
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
        self.base_url = "https://viacep.com.br/ws/{}/json/"
        self.max_retries = max_retries

    async def fetch_cep(self, session, cep):
        url = self.base_url.format(cep)

        async with self.semaphore:
            for attempt in range(self.max_retries):
                try:
                    async with session.get(url, timeout=10) as response:
                        if response.status == 200:
                            data = await response.json()
                            if data.get("erro"):
                                return {"cep": cep, "error": "CEP não encontrado/inexistente"}
                            return data

                        elif response.status == 429:
                            # Too Many Requests: Espera um tempo antes de tentar de novo
                            await asyncio.sleep(2 ** attempt)
                            continue

                        else:
                            return {"cep": cep, "error": f"Erro HTTP: {response.status}"}

                except asyncio.TimeoutError:
                    if attempt == self.max_retries - 1:
                        return {"cep": cep, "error": "Timeout da API ViaCEP"}
                    await asyncio.sleep(1)  # Espera antes de tentar de novo
                except Exception as e:
                    return {"cep": cep, "error": str(e)}

    async def process_ceps(self, cep_list):
        # TCPConnector limitando conexões simultâneas para otimizar uso de rede
        connector = aiohttp.TCPConnector(limit=100)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = [self.fetch_cep(session, str(cep).zfill(8)) for cep in cep_list]

            results = []
            total_tasks = len(tasks)
            completed = 0

            print()  # Dá uma quebra de linha antes de começar o progresso

            # as_completed nos entrega o resultado assim que a requisição termina
            for task in asyncio.as_completed(tasks):
                result = await task
                results.append(result)
                completed += 1

                # Atualiza a mesma linha do terminal a cada 50 CEPs processados
                if completed % 50 == 0 or completed == total_tasks:
                    percentual = (completed / total_tasks) * 100
                    print(f"\rProgresso: {completed}/{total_tasks} CEPs processados ({percentual:.1f}%)...", end="",
                          flush=True)

            print("\n")  # Quebra de linha ao finalizar 100%
            return results

    def run_extraction(self, cep_list):
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(self.process_ceps(cep_list))

        success_data = [r for r in results if "error" not in r]
        error_data = [r for r in results if "error" in r]

        return success_data, error_data