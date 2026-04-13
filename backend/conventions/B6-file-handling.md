# Convention B6: File Handling (Server-Side)

## Principle

Files go directly from the client to object storage (S3, GCS, Azure Blob) via presigned URLs. The server generates the URL and validates the file after upload. The server never proxies file content through itself — that wastes bandwidth, memory, and CPU. File type validation uses magic bytes (file signatures), not client-provided Content-Type headers which are trivially spoofed. Storage operations are wrapped behind an interface so the provider can be swapped. See also universal convention #9 for the client-side file upload pattern.

## Reusable System

Create a file handling foundation that establishes:
- A storage service interface (upload, download, delete, getSignedUrl) that wraps the cloud SDK
- Presigned URL generation with expiration (5-15 minutes), file type restrictions, and size limits
- Server-side file validation: magic byte inspection for MIME type, size verification, optional malware scan
- Storage key generation: server-side, UUID-based. Client never chooses the storage path.

## Rules

- Never proxy file uploads through the application server. Generate a presigned URL, let the client upload directly to storage.
- Generate storage keys server-side using UUIDs or structured paths. Never let the client specify the storage path (path traversal risk).
- Validate file type by inspecting magic bytes (file signatures), not by trusting the Content-Type header or file extension. A file named photo.jpg with Content-Type image/jpeg could be an executable.
- Validate file size server-side even if the presigned URL has a size limit.
- Wrap all storage operations behind a StorageService interface. Feature code calls the interface, never the AWS SDK or GCS client directly. The implementation can be swapped (local filesystem for development, S3 for production) without changing feature code.
- Keep presigned URL expiration short: 5-15 minutes for uploads, 1-5 minutes for downloads.

## Violations

- Handler receives the file as multipart upload, stores it in memory or /tmp, then uploads to S3. A 100MB file ties up a server process for the entire transfer. Two times the bandwidth.
- Content-Type header trusted for validation. A .exe file renamed to .jpg with a fake Content-Type passes validation.
- AWS S3 SDK imported directly in 15 different handler files. Switching to GCS requires changing 15 files.
- Client passes the desired filename as the storage key. Attacker passes ../../../etc/passwd.

## Wrong vs Right

- WRONG: client uploads file to API server → server saves to /tmp → server uploads to S3 → server responds. Double bandwidth, server memory spike, slow.
- RIGHT: client requests presigned URL from API → API validates request (user permissions, file type, size) → API generates presigned URL → client uploads directly to S3 → client notifies API of completion → API validates the uploaded file (magic bytes, size) and records it in the database.
- WRONG: if (file.mimetype === 'image/jpeg') — trusts the client-provided MIME type.
- RIGHT: read the first bytes of the file and compare against known magic byte signatures. JPEG starts with FF D8 FF. PNG starts with 89 50 4E 47. Use a library for this.

## Research Notes

When bootstrapping this convention:
- Research the cloud storage SDK for the project's cloud provider and how to generate presigned URLs.
- Research magic byte validation libraries for the language (file-type for Node, python-magic for Python, etc.).
- Research the framework's patterns for abstracting cloud services behind interfaces.
- Document the StorageService interface, presigned URL configuration, and validation rules in References.md.
