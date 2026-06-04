// Copyright 2026 The NATS Authors
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package server

import (
	"expvar"
	"runtime"
	"sync/atomic"
)

var diosWaitersExpvar = expvar.NewMap("io_waiters")

// Used to limit number of disk IO calls in flight since they could all be blocking an OS thread.
// https://github.com/nats-io/nats-server/issues/2742
type diskIOSemaphore struct {
	name    string
	ch      chan struct{}
	waiters atomic.Int64
}

func newDiskIOSemaphore(name string, n int) *diskIOSemaphore {
	d := &diskIOSemaphore{name: name, ch: make(chan struct{}, n)}
	for range n {
		d.ch <- struct{}{}
	}
	diosWaitersExpvar.Set(name, expvar.Func(func() any {
		return d.waiters.Load()
	}))
	return d
}

func defaultDiskIOSemaphore(name string) *diskIOSemaphore {
	// Limit ourselves to a sensible number of blocking I/O calls.
	// Range between 4-16 concurrent disk I/Os based on CPU cores,
	// or 50% of cores if greater than 32 cores.
	mp := runtime.GOMAXPROCS(-1)
	nIO := min(16, max(4, mp))
	if mp > 32 {
		// If the system has more than 32 cores then limit dios to 50% of cores.
		nIO = max(16, min(mp, mp/2))
	}
	return newDiskIOSemaphore(name, nIO)
}

func (d *diskIOSemaphore) acquire() {
	select {
	case <-d.ch:
		return
	default:
	}
	d.waiters.Add(1)
	<-d.ch
	d.waiters.Add(-1)
}

func (d *diskIOSemaphore) release() {
	d.ch <- struct{}{}
}

func (d *diskIOSemaphore) cap() int {
	return cap(d.ch)
}
