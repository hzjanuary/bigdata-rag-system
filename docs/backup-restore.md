# Backup and restore

Use only your trusted operator config. Backups contain plaintext source documents,
workspace capability hashes, jobs and extracted text. Store them mode 0700/0600,
encrypt them outside this tool if needed, and apply your own retention policy.
Neither the owner config/key nor model weights are bundled; preserve those
separately. The tool rejects symlink paths and existing backup destinations.

Stop the API before backup. The same exclusive instance lock prevents backup or
restore while the API is running. Keep Qdrant running on its private network.

For a local Python installation:

```bash
# Stop your rag serve process first.
uv run rag backup create --destination /absolute/private/new-backup
# Init a NEW installation; select its private config, with an EMPTY private Qdrant.
uv run rag --config /private/new-install/config.json backup restore \
  --source /absolute/private/new-backup
```

For Compose, stop just the API and run the CLI on that project's private network,
with the same UID and config/state mounts. In the example below PROJECT is your
explicit Compose project name (default workspace-rag), and the private directory
contains config/ and state/:

```bash
docker compose stop api
docker run --rm --network PROJECT_private --user "$(id -u):$(id -g)" \
  -v "$PWD/.local/operator:/private" workspace-rag-core:local \
  backup create --destination /private/backups/new-backup
# Start the existing API again after successful backup.
docker compose start api
```

Create exports a SQLite backup plus Qdrant vectors for exactly committed chunk
IDs into a new directory. It verifies every published chunk has a vector and
records file SHA-256, point count and index version in manifest.json. This is an
application-consistent logical index backup, not a Qdrant raw-volume copy or crash
snapshot. It omits unpublished orphan vectors, includes queued job input and job
history, and requires exclusive writers for the whole operation. Never run other
Qdrant writers directly against this installation while backing up.

Restore requires a newly initialized empty SQLite installation and no colliding
workspace collections in the target Qdrant. It checks file hashes, SQLite integrity,
embedding metadata, complete chunk-ID coverage and vector dimensions before
writing. It publishes SQLite only after all restored vectors acknowledge. Owner
credentials come from the NEW private config; original workspace capabilities
remain valid because their stored hashes are restored. Start the API only after
restore succeeds; pending work resumes under normal idempotent recovery.

A failed restore can leave staged vectors in the otherwise empty trial Qdrant;
the tool never erases those automatically or overwrites an existing installation.
Inspect the fixed error code and retry into another fresh isolated target. A failed
backup lacks a complete manifest and must not be treated as usable. Keep the old
installation intact until independent source hashes, manifests, jobs and retrieval
have been checked in the restored target. Secure deletion of SQLite free pages,
backups or storage-device blocks is outside this tool's deletion promise.

The local isolated acceptance campaign rehearses this with its own project volumes,
then verifies original source bytes, persisted chunks/ranking, job history and ACL.
It never attaches operator volumes. Consult release/verification.md for actual
results and identity. Do not use `docker compose down -v` on retained storage.
