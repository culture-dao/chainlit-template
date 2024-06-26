# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.5 build 343 ] 2024-06-12

### Added
- Vector store handler
- List all files in any vector store
- Remove all empty vector stores
- Assistant handler lists attached files

## [0.4.4 build 327] - 2021-06-11

### Added
- Speech to text integrations
### Fixed
- Bumped CL to rc4 to fix Literal SDK issue
- Handle unavailable threads on chat resume
### Changed
- Citations now return as simple markdown

## [0.4.3 build 259] - 2024-05-21

### Added
- File uploads from Chainlit to OAI Thread-specific vectorstore
- OAI Object Handler for Assistant state dumps and dynamic maps


## [0.4.2 build 193] - 2024-05-21

### Fixed
- Render annotations even if quote is missing

## [0.4.1 build 193] - 2024-05-20

### Fixed
- Chainlit messages streaming

## [0.4.0 build 191] - 2024-05-15

### Added
- Support for OAI Assistant Streaming
- Changelog
- Super awesome logo

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


