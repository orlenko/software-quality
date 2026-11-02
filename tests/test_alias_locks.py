"""Owned alias separation and nonblocking advisory-lock invariants."""
from __future__ import annotations

import fcntl
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

from quality_trust import Invalid, within
from quality.evidence import target_lock
from quality.external_store import overlaps, receive, load


class AliasSeparationTests(unittest.TestCase):
    def test_injected_ancestor_identity_and_safe_sibling(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary).resolve();common=root/"common";common.mkdir();alternate=root/"alternate";alternate.mkdir()
            child=alternate/"cache";child.mkdir();sibling=root/"sibling";sibling.mkdir()
            actual=Path.lstat;identity=common.lstat()
            def equivalent(path):return identity if path==alternate else actual(path)
            with patch.object(Path,"lstat",equivalent):
                self.assertFalse(within(common,child))
                self.assertTrue(within(child,common))
                self.assertTrue(overlaps(common,child))
                self.assertFalse(overlaps(common,sibling))

    def test_membership_propagates_inspection_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            with patch("quality_trust.outside_path",side_effect=Invalid("path-inspection-unavailable")):
                with self.assertRaisesRegex(Invalid,"path-inspection-unavailable"):within(root/"item",root)


class AliasLockTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name).resolve();self.state=self.root/"state";self.state.mkdir(mode=0o700)
        self.repo=self.root/"subject";self.repo.mkdir()

    def test_same_object_different_spelling_contends_and_releases(self) -> None:
        alias_repo=self.repo/".."/"subject";alias_state=self.state/".."/"state"
        with target_lock(self.state,self.repo):
            with self.assertRaisesRegex(Invalid,"target-run-already-active"):
                with target_lock(alias_state,alias_repo):self.fail("same directory object acquired twice")
        with target_lock(alias_state,alias_repo):pass

    def test_real_platform_state_and_subject_aliases_contend(self) -> None:
        state=Path('/System/Volumes/Data')/self.state.relative_to('/')
        subject=Path('/System/Volumes/Data')/self.repo.relative_to('/')
        if not state.exists() or not os.path.samefile(state,self.state):
            self.skipTest('no stable alternate root namespace available on this platform')
        with target_lock(self.state,self.repo):
            with self.assertRaisesRegex(Invalid,"target-run-already-active"):
                with target_lock(state,subject):self.fail("platform aliases did not serialize")
        with target_lock(state,subject):pass

    def test_second_lock_contention_releases_object_and_descriptors(self) -> None:
        with target_lock(self.state,self.repo):pass
        legacy=next(path for path in self.state.glob('target-*.lock') if not path.name.startswith('target-object-'))
        object_path=next(self.state.glob('target-object-v1-*.lock'))
        opened=[];actual_open=os.open
        def observed_open(*args,**kwargs):
            fd=actual_open(*args,**kwargs);opened.append(fd);return fd
        with legacy.open('r+b') as held:
            fcntl.flock(held,fcntl.LOCK_EX|fcntl.LOCK_NB)
            with patch('quality.evidence.os.open',side_effect=observed_open):
                with self.assertRaisesRegex(Invalid,'target-run-already-active'):
                    with target_lock(self.state,self.repo):self.fail('legacy contention ignored')
            for fd in opened:
                with self.assertRaises(OSError):os.fstat(fd)
            with object_path.open('r+b') as released:
                fcntl.flock(released,fcntl.LOCK_EX|fcntl.LOCK_NB)
        with target_lock(self.state,self.repo):pass

    def test_special_or_nonprivate_locks_refuse_without_blocking(self) -> None:
        with target_lock(self.state,self.repo):pass
        lock=next(self.state.glob('target-object-v1-*.lock'))
        lock.chmod(0o644)
        with self.assertRaises(Invalid):
            with target_lock(self.state,self.repo):self.fail('nonprivate lock accepted')
        lock.unlink();os.mkfifo(lock,0o600)
        started=time.monotonic()
        with self.assertRaises(Invalid):
            with target_lock(self.state,self.repo):self.fail('FIFO lock accepted')
        self.assertLess(time.monotonic()-started,1)
        lock.unlink();outside=self.root/'inert';outside.write_text('inert');lock.symlink_to(outside)
        with self.assertRaises(Invalid):
            with target_lock(self.state,self.repo):self.fail('symbolic lock accepted')

    def test_partial_interruption_closes_noninheritable_descriptors(self) -> None:
        opened=[];actual_open=os.open;actual_flock=fcntl.flock;calls=0
        def observed_open(*args,**kwargs):
            fd=actual_open(*args,**kwargs);opened.append(fd)
            self.assertFalse(os.get_inheritable(fd));return fd
        def interrupted(fd,operation):
            nonlocal calls
            calls+=1
            if calls==2:raise KeyboardInterrupt
            return actual_flock(fd,operation)
        with patch('quality.evidence.os.open',side_effect=observed_open),patch('quality.evidence.fcntl.flock',side_effect=interrupted):
            with self.assertRaises(KeyboardInterrupt):
                with target_lock(self.state,self.repo):self.fail('second acquisition interruption ignored')
        for fd in opened:
            with self.assertRaises(OSError):os.fstat(fd)
        with target_lock(self.state,self.repo):pass

    def test_malformed_plan_identifiers_have_no_identifier_lookups(self) -> None:
        for identifier in ('','../outside','a'*31,'a'*33,'G'*32,None,1):
            with self.subTest(identifier=identifier),patch.object(Path,'lstat',side_effect=AssertionError('identifier filesystem lookup')),patch('quality.external_store.target_lock') as lock:
                with self.assertRaises(Invalid):load(self.state,identifier)
                with self.assertRaises(Invalid):receive(self.state,identifier,None,None,None,None,[])
                lock.assert_not_called()
