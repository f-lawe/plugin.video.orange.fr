# 1.x

## [1.2.0](https://github.com/BreizhReloaded/plugin.video.orange.fr/releases/tag/v1.2.0) - 2021-03-12

### Added

- Provider interface to allow multi ISP support
- Support for Orange TV groups

### Changed

- Migrate current Orange integration to the new provider interface
- Update generators to write data from JSON-STREAMS and JSON-EPG formats
- Data files now written into user data folder

# 1.x

## [1.1.0](https://github.com/BreizhReloaded/plugin.video.orange.fr/releases/tag/v1.1.0) - 2021-03-04

### Added

- API calls to Orange now use a randomised user agent string

### Changed

- IPTV Manager integration refactoring
- Multi-days program load logic now embedded directly into Orange API client
- Log helper signature

### Fixed

- Programs responses reduced by half to avoid IncompleteRead error

## [1.0.0](https://github.com/BreizhReloaded/plugin.video.orange.fr/releases/tag/v1.0.0) - 2021-03-01

- Initial release
