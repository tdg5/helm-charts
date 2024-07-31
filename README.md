# helm-charts

Helm charts from various sources for various purposes.

## Charts

- [openvpn-as](./charts/openvpn-as)

## Development

### Git Hooks

A collection of recommended `git` hooks can be found in the `.githooks`
directory. These hooks can do useful things like ensuring that `make style`
succeeds before allowing a change to be committed.

By default, `git` ignores the hooks in the `.githooks` directory, but they can
be enabled by configuring your local repository with a `core.hooksPath` option
that targets the `.githooks` directory.

This can be accomplished using the `git` CLI like so:

```bash
git config --local core.hooksPath .githooks
```

Alternatively, you can update `.git/config` directly to add a `hooksPath`
option under the `core` section like so:

```
[core]
	hooksPath = .githooks
```

#### Commit without running pre-commit hooks

Sometimes it is useful to be able to force a commit into existence even if the
pre-commit hook is failing. This can be accomplished using the `git` CLI with
the `--no-verify` flag. For example, the following command will create a commit
without running the pre-commit hooks:

```bash
git commit -m "House on fire, WIP" --no-verify
```

In VSCode, similar functionality can be enabled by setting
`"git.allowNoVerifyCommit": true`. Once this is done, additional commit
commands (e.g. `Commit ... (No Verify)`) should become available that allow you
to commit without running the pre-commit hooks.
