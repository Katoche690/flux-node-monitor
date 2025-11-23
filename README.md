# Flux Node Monitor for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/Katoche690/flux-node-monitor.svg)](https://github.com/Katoche690/flux-node-monitor/releases)
[![License](https://img.shields.io/github/license/Katoche690/flux-node-monitor.svg)](LICENSE)

Intégration Home Assistant complète pour monitorer vos nodes Flux en temps réel.

![Flux Monitor Dashboard](images/dashboard.png)

## 🌟 Fonctionnalités

### 🖥️ Monitoring par Node
- ⏰ Prochain paiement estimé
- 🏆 Rank et Score en temps réel
- 🏷️ Tier (Cumulus/Nimbus/Stratus)
- 🌐 IP:Port
- 💾 Versions FluxOS et Benchmark
- ⚡ Performance (EPS, DWS, Download, Upload)
- 🕐 Uptime et stabilité
- 📱 Applications déployées
- 🔢 Blocs avant paiement

### 💰 Wallet
- 💵 Balance en FLUX et EUR
- 📈 Revenus mensuels
- 💱 Prix FLUX en temps réel
- 📊 Historique des transactions

### 🎨 Parallel Assets
- Nombre total d'assets
- Valeur totale
- Détails complets

### 🌍 Écosystème Flux
- Nombre de nodes Cumulus
- Nombre de nodes Nimbus
- Nombre de nodes Stratus
- Total du réseau

## 📦 Installation

### HACS (Recommandé)

1. Ouvrez HACS dans Home Assistant
2. Cliquez sur "Integrations"
3. Cliquez sur les 3 points en haut à droite
4. Sélectionnez "Custom repositories"
5. Ajoutez cette URL : `https://github.com/Katoche690/flux-node-monitor`
6. Catégorie : `Integration`
7. Cliquez sur "ADD"
8. Cherchez "Flux Node Monitor" et installez
9. Redémarrez Home Assistant

### Installation Manuelle

1. Téléchargez la [dernière release](https://github.com/Katoche690/flux-node-monitor/releases)
2. Copiez tous les fichiers (sauf README.md, LICENSE, etc.) dans votre dossier `config/custom_components/flux_monitor/`
3. Votre structure doit ressembler à :
   ```
   config/
   └── custom_components/
       └── flux_monitor/
           ├── __init__.py
           ├── config_flow.py
           ├── const.py
           ├── flux_api.py
           ├── manifest.json
           ├── sensor.py
           └── translations/
   ```
4. Redémarrez Home Assistant

## ⚙️ Configuration

1. Allez dans **Configuration** → **Intégrations**
2. Cliquez sur **+ Ajouter une intégration**
3. Cherchez **Flux Node Monitor**
4. Entrez votre adresse wallet Flux (commence par `t1`)
5. Entrez les IPs de vos nodes séparées par des virgules
   - Format : `192.168.1.100:16127,192.168.1.101:16127`
   - Port par défaut : `16127`

## 📊 Sensors Créés

L'intégration crée automatiquement **40+ sensors** :

### Par Node (Node 1, Node 2, etc.)
```
sensor.flux_node_1_next_payment
sensor.flux_node_1_rank
sensor.flux_node_1_tier
sensor.flux_node_1_score
sensor.flux_node_1_uptime
sensor.flux_node_1_eps
sensor.flux_node_1_dws
sensor.flux_node_1_download
sensor.flux_node_1_upload
sensor.flux_node_1_apps_count
... et plus
```

### Wallet
```
sensor.flux_wallet_balance
sensor.flux_wallet_balance_eur
sensor.flux_wallet_monthly_rewards
sensor.flux_wallet_monthly_rewards_eur
sensor.flux_wallet_flux_price
```

### Écosystème
```
sensor.flux_ecosystem_cumulus_nodes
sensor.flux_ecosystem_nimbus_nodes
sensor.flux_ecosystem_stratus_nodes
sensor.flux_ecosystem_total_nodes
```

## 📱 Exemples d'utilisation

### Dashboard Simple

```yaml
type: entities
title: Mes Nodes Flux
entities:
  - entity: sensor.flux_node_1_next_payment
    name: Prochain paiement
  - entity: sensor.flux_node_1_score
    name: Score
  - entity: sensor.flux_wallet_balance
    name: Balance
  - entity: sensor.flux_wallet_monthly_rewards
    name: Revenus mensuels
```

### Alerte Node Down

```yaml
automation:
  - alias: "Flux - Node Down"
    trigger:
      platform: numeric_state
      entity_id: sensor.flux_node_1_uptime
      below: 3600  # Moins d'1 heure
    action:
      service: notify.mobile_app
      data:
        title: "⚠️ Flux Node Alert"
        message: "Le Node 1 est down !"
```

### Notification Paiement Imminent

```yaml
automation:
  - alias: "Flux - Paiement Imminent"
    trigger:
      platform: numeric_state
      entity_id: sensor.flux_node_1_blocks_until_payment
      below: 10
    action:
      service: notify.mobile_app
      data:
        title: "💰 Paiement Imminent"
        message: "Paiement dans moins de 10 blocs !"
```

Plus d'exemples dans le dossier [examples/](examples/)

## 🎨 Dashboard Complet

Un dashboard complet est disponible dans [examples/dashboard.yaml](examples/dashboard.yaml)

Il comprend :
- Vue d'ensemble des nodes
- Statistiques wallet
- Graphiques de performance
- Informations écosystème

## 🔔 Automatisations

15+ automatisations prêtes à l'emploi dans [examples/automations.yaml](examples/automations.yaml) :

- Alerte node down
- Paiement imminent
- Score faible
- Paiement reçu
- Rapport quotidien
- Rapport hebdomadaire
- Variation de prix importante
- Et plus !

## 🔧 Configuration Avancée

### Changer la fréquence de mise à jour

Par défaut : 5 minutes. Pour modifier, éditez `custom_components/flux_monitor/__init__.py` :

```python
SCAN_INTERVAL = timedelta(minutes=5)  # Changez cette valeur
```

### Logs de débogage

Ajoutez dans `configuration.yaml` :

```yaml
logger:
  logs:
    custom_components.flux_monitor: debug
```

## 🛠️ APIs Utilisées

- **api.runonflux.io** - Données des nodes
- **explorer.runonflux.io** - Wallet et transactions
- **api.coingecko.com** - Prix FLUX en EUR

Toutes les APIs sont publiques et gratuites.

## 📈 Fonctionnalités à venir

- [ ] Support de plusieurs wallets
- [ ] Calcul de rentabilité (revenus - coûts)
- [ ] Prédictions via Machine Learning
- [ ] Export vers Grafana
- [ ] Notifications Discord/Telegram
- [ ] Interface de configuration avancée

Voir [ROADMAP.md](ROADMAP.md) pour plus de détails.

## 🐛 Rapport de bugs

Ouvrez une [issue](https://github.com/Katoche690/flux-node-monitor/issues) avec :
- Version de Home Assistant
- Version de l'intégration
- Logs complets
- Configuration utilisée

## 🤝 Contribution

Les contributions sont les bienvenues ! Voir [CONTRIBUTING.md](CONTRIBUTING.md)

## 📝 Changelog

Voir [CHANGELOG.md](CHANGELOG.md) pour l'historique des versions.

## 📄 License

MIT License - voir [LICENSE](LICENSE)

## ⭐ Support

Si ce projet vous aide, mettez-lui une étoile ⭐ !

Pour toute question, ouvrez une [discussion](https://github.com/Katoche690/flux-node-monitor/discussions)

## 🙏 Remerciements

- Équipe Flux pour les APIs publiques
- Communauté Home Assistant
- Tous les contributeurs

---

**Fait avec ❤️ pour la communauté Flux**
