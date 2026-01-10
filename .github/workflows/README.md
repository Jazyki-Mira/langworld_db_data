## GitHub Actions: cross-repo trigger ([dispatch-web.yml](dispatch-web.yml))

This is the “trigger” half of the automation chain: push data here → web repo workflow runs there, updating the `langworld_db_data` subtree and committing the result.

- Runs on every push to the `master` branch in this repo.
- Sends a [`repository_dispatch`](https://docs.github.com/actions/learn-github-actions/events-that-trigger-workflows#repository_dispatch) event to [`Jazyki-Mira/langworld_db_pyramid`](https://github.com/Jazyki-Mira/langworld_db_pyramid).
- Uses Peter Evans's [Repository Dispatch](https://github.com/peter-evans/repository-dispatch) GitHub Action that calls [GitHub API](https://docs.github.com/en/rest/repos/repos#create-a-repository-dispatch-event).
- Uses event type `langworld-data-updated` and includes the source commit SHA and ref in the payload (`client_payload`).
- Required secret: `LANGWORLD_WEB_UPDATE_PAT` — a fine-grained Personal Access Token with access to `Jazyki-Mira/langworld_db_pyramid` and repository permissions `Contents: Read and write`. The PAT is created in Developer Settings and added as an Actions repository secret in both `langworld_db_data` and `langworld_db_pyramid`.

> Note:`repository_dispatch` will only trigger a workflow run in `langworld_db_pyramid` if the workflow there is set up on the **default branch**.

### Example

- made [a commit](https://github.com/Jazyki-Mira/langworld_db_data/commit/06bb2629f90a7e4d303e759209d0602950f62a2f) in this repo to fix a typo in data
- [GitHub Action](https://github.com/Jazyki-Mira/langworld_db_data/actions/runs/20877364699) was run in this repo to dispatch an update to `langworld_db_pyramid`
- [GitHub Action](https://github.com/Jazyki-Mira/langworld_db_pyramid/actions/runs/20877366062) was triggered and run in the web repo
- [new commit was created in the web repo](https://github.com/Jazyki-Mira/langworld_db_pyramid/commit/e8318e71a02c1190b5df171d93f7f36ef9ab0163) to reflect that change
