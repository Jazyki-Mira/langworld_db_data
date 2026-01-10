## GitHub Actions: cross-repo trigger ([dispatch-web.yml](dispatch-web.yml))

This is the “trigger” half of the automation chain: push data here → web repo workflow runs there, updating the `langworld_db_data` subtree and committing the result.

- Runs on every push to the `master` branch in this repo.
- Sends a [`repository_dispatch`](https://docs.github.com/actions/learn-github-actions/events-that-trigger-workflows#repository_dispatch) event to [`Jazyki-Mira/langworld_db_pyramid`](https://github.com/Jazyki-Mira/langworld_db_pyramid).
- Uses Peter Evans's [Repository Dispatch](https://github.com/peter-evans/repository-dispatch) GitHub Action that calls [GitHub API](https://docs.github.com/en/rest/repos/repos#create-a-repository-dispatch-event).
- Uses event type `langworld-data-updated` and includes the source commit SHA and ref in the payload (`client_payload`).
- Required secret: `LANGWORLD_WEB_UPDATE_PAT` — a fine-grained Personal Access Token with access to `Jazyki-Mira/langworld_db_pyramid` and repository permissions `Contents: Read and write`. The PAT is created in Developer Settings and added as an Actions repository secret in both `langworld_db_data` and `langworld_db_pyramid`.

> Note:`repository_dispatch` will only trigger a workflow run in `langworld_db_pyramid` if the workflow there is set up on the **default branch**.