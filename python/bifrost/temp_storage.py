
# Copyright (c) 2016, The Bifrost Authors. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# * Neither the name of The Bifrost Authors nor the names of its
#   contributors may be used to endorse or promote products derived
#   from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import bifrost as bf

import threading

from bifrost import telemetry
telemetry.track_module()

class TempStorage(object):
    def __init__(self, space):
        self.space = space
        self.size  = 0
        self.ptr   = None
        self.lock  = threading.Lock()
    def __del__(self):
        self._free()
    def allocate(self, size):
        return TempStorageAllocation(self, size)
    def _allocate(self, size):
        if size > self.size:
            self._free()
            self.ptr = bf.memory.raw_malloc(size, self.space)
            self.size = size
    def _free(self):
        if self.ptr:
            bf.memory.raw_free(self.ptr, self.space)
            self.ptr  = None
            self.size = 0
class TempStorageAllocation(object):
    def __init__(self, parent, size):
        self.parent = parent
        self.parent.lock.acquire()
        self.parent._allocate(size)
        self.size = parent.size
        self.ptr  = parent.ptr
    def release(self):
        self.parent.lock.release()
    def __enter__(self):
        return self
    def __exit__(self, type, value, tb):
        self.release()
