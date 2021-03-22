## [Unreleased]()

### Fixed

- Channel groups for basic integration
- Settings translations

# 1.x

## [1.2.1](https://github.com/BreizhReloaded/plugin.video.orange.fr/releases/tag/v1.2.0) - 2021-03-14

### Added

- French translations for settings and dialogs

### Changed

- EPG now loaded following TV Guide past and future days settings 

### Fixed

- Audio doesn't drop anymore when timeshifting ([issue #612](https://github.com/xbmc/inputstream.adaptive/issues/612))

### Removed

- Remove basic interval setting (now use TV Guide update value)

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
