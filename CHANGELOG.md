# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
### Fixed
### Changed
### Removed

## [0.4.188] - 2024-05-15

### Added
- Support for OAI Assistant Streaming
- Changelog

### Changed
- Updated Readme

## [0.3.2] - 2024-05-02

### Fixed: 
- OAI returns invalid Pydantic models
- Fix tests

## [0.3.1] - 2024-04-25

### Added

- Dynamic Names
- Add oauth_callback.py, discord and mailchimp hooks
- Add tests from AFGE
- Chainlit run
- Bump OAI
- Test-assistant complete
- Updated infra related folders
- Update .gitignore
- Update readmes

### Fixed

- Add utils for annotations
- Update OAI Types
- Agent run success
- Wrong test directory; types
- Fixing fixtures
- OAI util actually loads the API key from dir
- Refactor to match new annotations adapter
- Test assistant/ test runs
- File handler
- Anonymize
- Correct Dockerfile
- Remove /app
- Deploy scripts point to OAI assistant folder
- Remove incorrect .chainlit folder
- Remove old Dockerfile

### Changed

- Broken tests
- Use OAI util client, rename types
- Update chainlit tests


## [0.3.0] - 2024-04-25

### Added

- Initial project setup commands
- Added build scripts
- Terraform variables
- Cloudbuild variables

### Fixed

- Docker build contains environment variables
- Dockerfile should be in app
- Changed app location in load_secrets
- Environment sample
- Environment import consistency
- Add service account to secrets accessor

### Refactored

- Cloudbuild 'staging', not 'latest'


## [0.2.0] - 2024-03-28

### Added

- OAI Assistant file retrieval returns annotations
- File retrieval tools to load files
- Literal utils

## [0.1.0] - 2024-02-28

### Added

- Docker build and test assistant
- Public access to Cloud Run deploys
- Load environment variables into GCS Secret Manager

### Fixed

- Update proper project ID and required APIs
- Dockerfile app & context

### Changed

- Cloud Run


