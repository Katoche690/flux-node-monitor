# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-11-23

### Added
- Initial release
- Support for multiple Flux nodes monitoring
- Real-time node performance metrics (EPS, DWS, Download, Upload)
- Wallet balance and monthly rewards tracking
- Price monitoring (FLUX to EUR)
- Parallel Assets support
- Ecosystem statistics (Cumulus, Nimbus, Stratus nodes count)
- Next payment estimation
- Node rank and score tracking
- Uptime monitoring
- FluxOS and Benchmark version tracking
- Apps deployment monitoring
- Configuration via Home Assistant UI
- French translation
- 40+ sensors automatically created
- HACS support

### APIs Used
- api.runonflux.io - Node data
- explorer.runonflux.io - Wallet and transactions
- api.coingecko.com - FLUX price

### Notes
- Update interval: 5 minutes
- Supports multiple nodes per installation
- Compatible with Home Assistant 2023.1.0+

## [Unreleased]

### Planned Features
- Multi-wallet support
- Profitability calculator (rewards - costs)
- Machine Learning predictions
- Grafana export
- Discord/Telegram notifications
- Advanced configuration interface
- Historical data retention
- Custom update intervals per sensor
- Node comparison dashboard
- Alert customization

---

For more information, see the [ROADMAP](ROADMAP.md)
