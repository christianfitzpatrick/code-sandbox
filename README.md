# Remote Code Execution Sandbox

A simple, work-in-progress system for executing arbitrary source code submitted over an API

The primary mechanism for isolation and security is Docker

Requests are separated into two categories:
 1. Interpreted implementations:
	* A source file can be passed directly to a Docker image for its runtime
 2. Compiled implementations
	 * This requires both building and running output, so a container is built from a temporary Dockerfile
	* The compilation and execution happens in the Docker container, and the server is simply handed back the standard output/standard error

## NOTES
* The `node_modules` folder in `tmp_src` is empty, but exists to satisfy the Docker `node` runtime
* The current model for language/runtime support is likely to be redesigned as the amount of supported languages grows
* An asynchronous message-queue implementation is currently in the works
