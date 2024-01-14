import enum
import pygit2

class PullResult(enum.Enum):
    up_to_date = 0
    fast_forwarded = 1
    merged = 2
    conflicted = 3
    merge_failed = 4
    fast_forward_failed = 5
    fetch_failed = 6
    missing_upstream_branch = 7

class AcceptCertCallbacks(pygit2.RemoteCallbacks):
    def certificate_check(self, certificate, valid, host):
        return True

def pull(repo):
    branch = repo.branches[repo.head.shorthand]
    print("Fetching changes...")
    # Handles broken support for shallow clones.
    try:
        repo.remotes[branch.upstream.remote_name].fetch(callbacks=AcceptCertCallbacks(), prune=pygit2.GIT_FETCH_PRUNE)
    except Exception as ex:
        print("Fetch failed: %s"%ex)
        return PullResult.fetch_failed
    upstream = branch.upstream
    if upstream is None:
        print("No upstream branch found.")
        return PullResult.missing_upstream_branch
    remote_master_id = upstream.target
    merge_result, _ = repo.merge_analysis(remote_master_id)
    # Up to date, do nothing
    if merge_result & pygit2.GIT_MERGE_ANALYSIS_UP_TO_DATE:
        print("Up-to date.")
        return PullResult.up_to_date
    elif merge_result & pygit2.GIT_MERGE_ANALYSIS_FASTFORWARD:
        print("Doing a fast forward...")
        try:
            repo.checkout_tree(upstream.peel())
        except:
            return PullResult.fast_forward_failed
        branch.set_target(upstream.target)
        repo.head.set_target(upstream.target)
        return PullResult.fast_forwarded
    elif merge_result & pygit2.GIT_MERGE_ANALYSIS_NORMAL:
        try:
            repo.merge(remote_master_id)
        except:
            return PullResult.merge_failed
        if repo.index.conflicts is not None:
            return PullResult.conflicted
        user = repo.default_signature
        tree = repo.index.write_tree()
        commit = repo.create_commit('HEAD', user, user, 'Merge!', tree, [repo.head.target, remote_master_id])
        # We need to do this or git CLI will think we are still merging.
        repo.state_cleanup()
        return PullResult.merged
    else:
        raise AssertionError('Unknown merge analysis result')
