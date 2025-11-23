"""
Flux Node Monitor API Client
Monitore les nodes Flux et l'écosystème global
"""
import aiohttp
import asyncio
from datetime import datetime, timedelta
import logging

_LOGGER = logging.getLogger(__name__)

# URLs de l'API Flux
FLUXNODES_API = "https://api.runonflux.io"
EXPLORER_API = "https://explorer.runonflux.io/api"

class FluxMonitor:
    def __init__(self, wallet_address, node_ips=None):
        """
        Initialise le moniteur Flux
        
        Args:
            wallet_address: Adresse du wallet Flux
            node_ips: Liste des IPs des nodes (format ["ip:port", "ip:port"])
        """
        self.wallet_address = wallet_address
        self.node_ips = node_ips or []
        self.session = None
        
    async def _get_session(self):
        """Crée ou retourne la session aiohttp"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """Ferme la session"""
        if self.session:
            await self.session.close()
            
    async def _api_call(self, url, endpoint):
        """Effectue un appel API"""
        session = await self._get_session()
        try:
            async with session.get(f"{url}{endpoint}", timeout=30) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    _LOGGER.error(f"Erreur API {response.status}: {endpoint}")
                    return None
        except Exception as e:
            _LOGGER.error(f"Erreur lors de l'appel API {endpoint}: {e}")
            return None
    
    async def get_flux_price(self):
        """Récupère le prix actuel du FLUX en EUR"""
        try:
            session = await self._get_session()
            async with session.get("https://api.coingecko.com/api/v3/simple/price?ids=zelcash&vs_currencies=eur", timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('zelcash', {}).get('eur', 0)
        except Exception as e:
            _LOGGER.error(f"Erreur récupération prix: {e}")
        return 0
    
    async def get_node_info(self, node_ip):
        """
        Récupère les informations détaillées d'un node
        
        Args:
            node_ip: IP du node (format "ip:port")
        """
        # Informations du node depuis l'API FluxNodes
        node_data = await self._api_call(FLUXNODES_API, f"/daemon/viewdeterministiczelnodelist?filter={node_ip.split(':')[0]}")
        
        if not node_data or 'data' not in node_data or not node_data['data']:
            _LOGGER.error(f"Impossible de récupérer les données pour {node_ip}")
            return None
        
        # Prend le premier résultat qui correspond
        node = None
        for n in node_data['data']:
            if node_ip in n.get('ip', ''):
                node = n
                break
        
        if not node:
            _LOGGER.error(f"Node {node_ip} non trouvé dans la liste")
            return None
        
        # Récupère les benchmarks
        benchmark_data = await self._api_call(FLUXNODES_API, f"/flux/benchmarks")
        benchmark = None
        if benchmark_data and 'data' in benchmark_data:
            for b in benchmark_data['data']:
                if b.get('ip', '').startswith(node_ip.split(':')[0]):
                    benchmark = b
                    break
        
        # Calcul du prochain paiement (estimation basée sur le dernier paid height)
        current_height_data = await self._api_call(FLUXNODES_API, "/daemon/getblockcount")
        current_height = current_height_data.get('data', 0) if current_height_data else 0
        
        last_paid = node.get('lastpaidheight', 0)
        blocks_until_payment = 0
        next_payment_time = "Inconnu"
        
        if current_height > 0 and last_paid > 0:
            # Estimation: un node est payé environ toutes les 2 heures (dépend du nombre de nodes)
            # Un block = ~2 minutes
            blocks_until_payment = max(0, 60 - (current_height - last_paid))  # Approximation
            minutes_until_payment = blocks_until_payment * 2
            next_payment_time = str(timedelta(minutes=minutes_until_payment))
        
        # Tier du node
        tier = node.get('tier', 'unknown').upper()
        
        # Construction des données
        node_info = {
            'ip_port': node.get('ip', node_ip),
            'tier': tier,
            'rank': node.get('rank', 'N/A'),
            'next_payment': next_payment_time,
            'blocks_until_payment': blocks_until_payment,
            'last_paid_height': last_paid,
            'added_height': node.get('addedheight', 0),
            'last_confirmed_height': node.get('lastconfirmedheight', 0),
            'collateral': node.get('collateral', 'N/A'),
            'txhash': node.get('txhash', 'N/A'),
        }
        
        # Ajoute les données de benchmark si disponibles
        if benchmark:
            node_info.update({
                'flux_os_version': benchmark.get('flux', {}).get('version', 'N/A'),
                'benchmark_version': benchmark.get('bench', {}).get('version', 'N/A'),
                'eps': benchmark.get('bench', {}).get('eps', 0),
                'dws': benchmark.get('bench', {}).get('ddwrite', 0),
                'download': benchmark.get('bench', {}).get('download', 0),
                'upload': benchmark.get('bench', {}).get('upload', 0),
                'last_benchmark': benchmark.get('bench', {}).get('time', 'N/A'),
                'uptime': benchmark.get('node', {}).get('uptime', 0),
                'score': benchmark.get('bench', {}).get('status', 'N/A'),
                'apps': len(benchmark.get('apps', [])),
                'apps_list': [app.get('name', 'unknown') for app in benchmark.get('apps', [])],
            })
        else:
            node_info.update({
                'flux_os_version': 'N/A',
                'benchmark_version': 'N/A',
                'eps': 0,
                'dws': 0,
                'download': 0,
                'upload': 0,
                'last_benchmark': 'N/A',
                'uptime': 0,
                'score': 'N/A',
                'apps': 0,
                'apps_list': [],
            })
        
        return node_info
    
    async def get_wallet_info(self):
        """Récupère les informations du wallet"""
        # Balance du wallet
        balance_data = await self._api_call(EXPLORER_API, f"/addr/{self.wallet_address}/balance")
        balance = float(balance_data) / 100000000 if balance_data else 0  # Conversion satoshi vers FLUX
        
        # Prix du FLUX
        flux_price = await self.get_flux_price()
        balance_eur = balance * flux_price
        
        # Récupère les transactions pour calculer les revenus mensuels
        # On prend les 1000 dernières transactions
        tx_data = await self._api_call(EXPLORER_API, f"/txs?address={self.wallet_address}&pageNum=0")
        
        monthly_flux = 0
        if tx_data and 'txs' in tx_data:
            # Calcule les revenus des 30 derniers jours
            thirty_days_ago = datetime.now() - timedelta(days=30)
            for tx in tx_data['txs']:
                tx_time = datetime.fromtimestamp(tx.get('blocktime', 0))
                if tx_time >= thirty_days_ago:
                    # Calcule le montant reçu
                    for vout in tx.get('vout', []):
                        if self.wallet_address in vout.get('scriptPubKey', {}).get('addresses', []):
                            monthly_flux += float(vout.get('value', 0))
        
        monthly_eur = monthly_flux * flux_price
        
        return {
            'balance_flux': balance,
            'balance_eur': balance_eur,
            'monthly_flux': monthly_flux,
            'monthly_eur': monthly_eur,
            'flux_price_eur': flux_price,
        }
    
    async def get_parallel_assets(self):
        """Récupère les Parallel Assets du wallet"""
        # Note: L'API pour les Parallel Assets peut varier
        # Ceci est une structure de base à adapter selon l'API disponible
        pa_data = await self._api_call(FLUXNODES_API, f"/flux/parallelassets/{self.wallet_address}")
        
        if pa_data and 'data' in pa_data:
            assets = pa_data['data']
            total_value = sum(asset.get('amount', 0) for asset in assets)
            
            return {
                'total_assets': len(assets),
                'total_value': total_value,
                'assets_detail': assets,
            }
        
        return {
            'total_assets': 0,
            'total_value': 0,
            'assets_detail': [],
        }
    
    async def get_ecosystem_stats(self):
        """Récupère les statistiques globales de l'écosystème Flux"""
        nodes_data = await self._api_call(FLUXNODES_API, "/daemon/viewdeterministiczelnodelist")
        
        if not nodes_data or 'data' not in nodes_data:
            return {
                'cumulus': 0,
                'nimbus': 0,
                'stratus': 0,
                'total': 0,
            }
        
        cumulus = sum(1 for node in nodes_data['data'] if node.get('tier') == 'CUMULUS')
        nimbus = sum(1 for node in nodes_data['data'] if node.get('tier') == 'NIMBUS')
        stratus = sum(1 for node in nodes_data['data'] if node.get('tier') == 'STRATUS')
        
        return {
            'cumulus': cumulus,
            'nimbus': nimbus,
            'stratus': stratus,
            'total': cumulus + nimbus + stratus,
        }
    
    async def get_all_data(self):
        """Récupère toutes les données en parallèle"""
        tasks = []
        
        # Nodes individuels
        nodes_data = []
        for node_ip in self.node_ips:
            tasks.append(self.get_node_info(node_ip))
        
        # Wallet info
        tasks.append(self.get_wallet_info())
        
        # Parallel Assets
        tasks.append(self.get_parallel_assets())
        
        # Ecosystem stats
        tasks.append(self.get_ecosystem_stats())
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Sépare les résultats
        nodes_data = results[:len(self.node_ips)]
        wallet_info = results[len(self.node_ips)]
        parallel_assets = results[len(self.node_ips) + 1]
        ecosystem_stats = results[len(self.node_ips) + 2]
        
        return {
            'nodes': [n for n in nodes_data if n is not None and not isinstance(n, Exception)],
            'wallet': wallet_info if not isinstance(wallet_info, Exception) else {},
            'parallel_assets': parallel_assets if not isinstance(parallel_assets, Exception) else {},
            'ecosystem': ecosystem_stats if not isinstance(ecosystem_stats, Exception) else {},
            'timestamp': datetime.now().isoformat(),
        }
